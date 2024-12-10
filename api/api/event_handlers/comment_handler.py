import uuid

from api.event_handlers.base_handler import BaseEventHandler
from api.models.webhook_payloads import BookStackRelatedItem, BookStackWebhookPayload
from shared.bookstack_client import AgentBookStackClient
from shared.constants import PROJECT_REQUIREMENTS_PAGE_NAME
from shared.models import ProjectContextInfo, WikiContextInfo
from shared.utils import get_project_metadata_for_page


class CommentEventHandler(BaseEventHandler):

    confirmation_response: str = """<p>Comment received! Processing... (<strong>Job ID:</strong>{job_id})</p>
<p><a href="/cancel/{job_id}">Cancel this execution</a> | <a href="{tape_link}">View Agent's Tape</a></p>
"""

    def handle_comment_create(self, event: BookStackWebhookPayload):
        print(event)
        if event.related_item.entity_type == "page":
            comment = (
                event.related_item.html.replace("<p>", "").replace("</p>", "").strip()
            )
            wiki_context = self.get_wiki_context(event)
            print(wiki_context)
            if wiki_context.page_name == PROJECT_REQUIREMENTS_PAGE_NAME:
                if comment.startswith("/next"):
                    job = self.agents_queue.enqueue(
                        "agents.wikiagent.project_agent.agent.react_to_comment",
                        kwargs={"wiki_context": wiki_context, "comment": comment},
                    )
            else:
                tape_page = None
                if event.related_item.parent_id is None:
                    tape_page = self.create_tape_page(wiki_context)
                    if tape_page:
                        wiki_context.tape_page_id = tape_page["id"]

                job = self.agents_queue.enqueue(
                    "agents.wikiagent.comment_agent.react_to_comment",
                    kwargs={"wiki_context": wiki_context, "comment": comment},
                )
                if tape_page:
                    self.client.create_comment(
                        self.confirmation_response.format(
                            job_id=job.id, tape_link=f"/link/{tape_page['id']}"
                        ),
                        page_id=event.related_item.entity_id,
                        parent_id=event.related_item.local_id,
                    )
                    # TODO Update confirmation comment when execution has finished

    def handle_commented_on(self, event: BookStackWebhookPayload):
        print("COMMENTED_ON EVENT")
        print(event)

    def get_wiki_context(self, event: BookStackWebhookPayload):
        page_id = event.related_item.entity_id
        page = self.client.get_page(page_id)
        project_metadata = get_project_metadata_for_page(page_id)
        context = WikiContextInfo(
            type="comment_created",
            user_id=event.triggered_by["id"],
            page_id=event.related_item.entity_id,
            page_name=page["name"],
            book_id=page["book_id"],
            local_comment_id=event.related_item.local_id,
            project_id=project_metadata["project_id"] if project_metadata else None,
            project_name=project_metadata["project_name"] if project_metadata else None,
            tags=page["tags"],
            project_context=ProjectContextInfo(
                project_id=project_metadata["project_id"],
                metadata_book_id=project_metadata["metadata_book"]["id"],
                creative_agents_chapter_id=project_metadata["creative_agents"][
                    "chapter_id"
                ],
                integrity_agents_chapter_id=project_metadata["integrity_agents"][
                    "chapter_id"
                ],
                involved_agents_chapter_id=project_metadata["involved_agents"][
                    "chapter_id"
                ],
                tapes_chapter_id=project_metadata["tapes"]["chapter_id"],
            )
            if project_metadata
            else None,
        )
        return context

    def create_tape_page(self, context: WikiContextInfo):
        if context.project_id is None:
            return
        tape_page = self.client.create_page(
            book_id=context.project_context.metadata_book_id,
            chapter_id=context.project_context.tapes_chapter_id,
            name=f"Comment #{context.local_comment_id} on page {context.page_name}",
            markdown="The tape has not been uploaded yet. This typically means that the agent workflow is still running.",
        )
        return tape_page

    # def create_tape_page(self, event: BookStackWebhookPayload):
    #     page_id = event.related_item.entity_id
    #     page_name = self.client.get_page(page_id)["name"]
    #     project_metadata = get_project_metadata_for_page(page_id)
    #     if project_metadata is None:
    #         return
    #     project_metadata["tapes"]["chapter_id"]
    #     tape_page = self.client.create_page(
    #         book_id=project_metadata["metadata_book"]["id"],
    #         chapter_id=project_metadata["tapes"]["chapter_id"],
    #         name=f"Comment #{event.related_item.local_id} on page {page_name}",
    #         markdown="The tape has not been uploaded yet. This typically means that the agent workflow is still running."
    #     )
    #     return tape_page
