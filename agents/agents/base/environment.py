import logging

from agents.wikiagent.project_agent.steps import *
from redis import Redis
from rq import Queue
from tapeagents.core import Action
from tapeagents.environment import Environment
from tapeagents.utils import FatalError

from shared.agents_redis_cache import AgentsRedisCache
from shared.bookstack_client import AgentBookStackClient
from shared.models import AgentType
from agents.base.steps import *
from agents.base.tape import WikiAgentsTape

logger = logging.getLogger(__name__)


class WikiAgentsEnvironment(Environment):
    def __init__(self, agent_name: str):
        super().__init__()
        self.client = AgentBookStackClient(agent_name)
        self.queue = Queue("tools-queue", Redis("redis", 6379), is_async=False)

    def react(self, tape: WikiAgentsTape) -> WikiAgentsTape:
        actions = [
            step
            for step in tape.steps[-tape.metadata.n_added_steps :]
            if isinstance(step, Action)
        ]
        for action in actions:
            try:
                match action:
                    case CreateBookAction():
                        book = self.client.create_book(
                            name=action.name,
                            description=action.description,
                            tags=action.tags,
                        )
                        tape = tape.append(CreateBookObservation(book_id=book["id"]))
                    case ReadBookAction():
                        book = self.client.get_book(action.book_id)
                        chapters = []
                        pages = []
                        for p in book["contents"]:
                            if p["type"] == "page":
                                pages.append(
                                    {
                                        "chapter_id": p["chapter_id"],
                                        "page_id": p["id"],
                                        "name": p["name"],
                                    }
                                )
                            elif p["type"] == "chapter":
                                chapters.append(
                                    {"chapter_id": p["id"], "name": p["name"]}
                                )
                                pages += [
                                    {
                                        "chapter_id": pp["chapter_id"],
                                        "page_id": pp["id"],
                                        "name": pp["name"],
                                    }
                                    for pp in p["pages"]
                                ]
                        tape = tape.append(
                            BookOverviewObservation(chapters=chapters, pages=pages)
                        )
                    case UpdateBookAction():
                        self.client.update_book(
                            book_id=action.book_id,
                            description=action.description,
                            tags=action.tags,
                        )
                        tape = tape.append(
                            UpdateBookObservation(content="Book updated!")
                        )
                    case DeleteBookAction():
                        self.client.delete_book(book_id=action.book_id)
                        tape = tape.append(
                            DeleteBookObservation(content="Book deleted!")
                        )
                    case CreateChapterAction():
                        chapter = self.client.create_chapter(
                            book_id=action.book_id,
                            name=action.name,
                            description=action.description,
                            tags=action.tags,
                        )
                        tape = tape.append(
                            CreateChapterObservation(chapter_id=chapter["id"])
                        )
                    case ReadChapterAction():
                        chapter = self.client.get_chapter(chapter_id=action.chapter_id)
                        tape = tape.append(
                            ChapterOverviewObservation(
                                name=chapter["name"],
                                description=chapter["description"],
                                pages=[
                                    {
                                        "chapter_id": p["chapter_id"],
                                        "page_id": p["id"],
                                        "name": p["name"],
                                    }
                                    for p in chapter["pages"]
                                ],
                                tags=chapter["tags"],
                            )
                        )
                    case UpdateChapterDescriptionAction():
                        self.client.update_chapter(
                            chapter_id=action.chapter_id,
                            name=action.name,
                            description=action.description,
                            tags=action.tags,
                        )
                        tape = tape.append(
                            UpdateChapterObservation(content="Chapter updated!")
                        )
                    case DeleteChapterAction():
                        self.client.delete_chapter(chapter_id=action.chapter_id)
                        tape = tape.append(
                            DeleteChapterObservation(content="Chapter deleted!")
                        )
                    case CreatePageAction():
                        page = self.client.create_page(
                            book_id=action.book_id,
                            chapter_id=action.chapter_id,
                            name=action.name,
                            markdown=action.content,
                            tags=action.tags,
                        )
                        tape = tape.append(CreatePageObservation(page_id=page["id"]))
                    case ReadPageAction():
                        page = self.client.get_page(page_id=action.page_id)
                        tape = tape.append(
                            ReadPageObservation(
                                content=page["markdown"], tags=page["tags"]
                            )
                        )
                    case UpdatePageContentAction():
                        self.client.update_page(
                            page_id=action.page_id,
                            chapter_id=action.chapter_id,
                            name=action.name,
                            markdown=action.content,
                            tags=action.tags,
                        )
                        tape = tape.append(
                            UpdatePageObservation(content="Page updated!")
                        )
                    case DeletePageAction():
                        self.client.delete_page(page_id=action.page_id)
                        tape = tape.append(
                            DeletePageObservation(content="Page deleted!")
                        )
                    case CreateCommentAction():
                        comment_id = self.client.create_comment(
                            text=action.comment,
                            page_id=action.page_id,
                            parent_id=action.parent_comment_id,
                        )
                        tape = tape.append(
                            CreateCommentObservation(comment_id=int(comment_id))
                        )
                    case ReadCommentsAction():
                        pass
                    case ReadCommentReplyAction():
                        pass
                    case LLMOutputParsingFailureAction():
                        pass
                    case UserDefinedTool():
                        job = self.queue.enqueue(
                            "tools.userdefined_tool.run",
                            timeout=600,
                            kwargs={
                                "tool_name": action.tool_name,
                                "parameters": action.parameters,
                            },
                        )
                        if job.get_status().value == "failed":
                            output = job.exc_info
                        elif job.get_status().value == "finished":
                            output = job.result if job.result else "Tool returned None"
                        tape = tape.append(UserDefinedToolObservation(output=output))

            except FatalError:
                raise
            except Exception as e:
                logger.exception(f"Error during action execution: {e}")
                tape = tape.append(ActionExecutionFailure(error=str(e)))
                break
        return tape
