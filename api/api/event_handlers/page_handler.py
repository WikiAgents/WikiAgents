from typing import List
from api.event_handlers.base_handler import BaseEventHandler
from api.models.webhook_payloads import BookStackWebhookPayload
from shared.agent_onboarding import AgentOnboarding

# from shared.agent_onboarding import generate_agent_user, set_agent_details, offboard_agent
from shared.models import AgentType, RedisAgent
from shared.utils import parse_agent_markdown, extract_code
from shared.agents_redis_cache import AgentsRedisCache
from shared.tools_redis_cache import ToolsRedisCache
from shared.constants import (
    TOOL_CREATE_COMMENT,
    TOOL_FAILED_COMMENT,
    TOOL_UPDATE_COMMENT,
    PROJECT_REQUIREMENTS_PAGE_NAME,
)
from shared.utils import get_project_metadata_for_page
from shared.models import WikiContextInfo, ProjectContextInfo
from shared.utils import extract_section_content, extract_code
import json

CONTENT_TASK_AGENTS_BOOK_ID = 1
TOOLS_BOOK_ID = 2
CREATIVE_FEEDBACK_GROUPS_BOOK_ID = 3
CONTENT_INTEGRITY_AGENTS_BOOK_ID = 4


class PageEventHandler(BaseEventHandler):
    def handle_page_create(self, event: BookStackWebhookPayload):
        page = self.client.get_page(event.related_item.id)
        if event.related_item.book_id == CONTENT_TASK_AGENTS_BOOK_ID:
            description, code_path, command, parameters, tools = parse_agent_markdown(
                page["markdown"]
            )
            AgentOnboarding().onboard_agent(
                RedisAgent(
                    type="content_agent",
                    name=page["name"],
                    page_id=page["id"],
                    description=description,
                    code_path=code_path,
                    command=command,
                    parameters=parameters,
                    tools=tools,
                )
            )

        elif event.related_item.book_id == CREATIVE_FEEDBACK_GROUPS_BOOK_ID:
            if page["chapter_id"] > 0:
                self.agents_queue.enqueue(
                    "agents.creative_feedback_agents.tinytroupe.personas.create_persona",
                    kwargs={"page_id": page["id"], "chapter_id": page["chapter_id"]},
                )
            else:
                try:
                    self.client.create_comment(
                        "💥 Creative Agents must be created inside a chapter!",
                        page_id=page["id"],
                    )
                except:
                    pass
        elif event.related_item.book_id == CONTENT_INTEGRITY_AGENTS_BOOK_ID:
            description, code_path, command, parameters, tools = parse_agent_markdown(
                page["markdown"]
            )
            AgentOnboarding().onboard_agent(
                RedisAgent(
                    type="integrity_agent",
                    name=page["name"],
                    page_id=page["id"],
                    description=description,
                    code_path=code_path,
                    command=command,
                    parameters=parameters,
                    tools=tools,
                )
            )
        elif event.related_item.book_id == TOOLS_BOOK_ID:
            tool_code = extract_code(page["markdown"])
            if tool_code:
                updated, error = ToolsRedisCache().update_tool(
                    page["name"], page["id"], code=tool_code
                )
                if updated:
                    self.client.create_comment(TOOL_CREATE_COMMENT, page_id=page["id"])
                else:
                    self.client.create_comment(
                        TOOL_FAILED_COMMENT + error, page_id=page["id"]
                    )
            else:
                self.client.create_comment(TOOL_FAILED_COMMENT, page_id=page["id"])
                # TODO generate tool

    def handle_page_update(self, event: BookStackWebhookPayload):
        if event.related_item.book_id in [
            CONTENT_TASK_AGENTS_BOOK_ID,
            CONTENT_INTEGRITY_AGENTS_BOOK_ID,
            CREATIVE_FEEDBACK_GROUPS_BOOK_ID,
        ]:
            page = self.client.get_page(event.related_item.id)
            description, code_path, command, parameters, tools = parse_agent_markdown(
                page["markdown"]
            )
            AgentsRedisCache().update_agent(
                RedisAgent(
                    name=page["name"],
                    description=description,
                    code_path=code_path,
                    command=command,
                    parameters=parameters,
                    tools=tools,
                )
            )
        elif event.related_item.book_id == TOOLS_BOOK_ID:
            page = self.client.get_page(event.related_item.id)
            tool_code = extract_code(page["markdown"])
            if tool_code:
                updated, error = ToolsRedisCache().update_tool(
                    page["name"], page["id"], code=tool_code
                )
                if updated:
                    self.client.create_comment(TOOL_UPDATE_COMMENT, page_id=page["id"])
                else:
                    self.client.create_comment(
                        TOOL_FAILED_COMMENT + error, page_id=page["id"]
                    )
            else:
                self.client.create_comment(TOOL_FAILED_COMMENT, page_id=page["id"])

        elif event.related_item.name == PROJECT_REQUIREMENTS_PAGE_NAME:
            page = self.client.get_page(event.related_item.id)
            if page["markdown"].startswith("### Step 1/5"):
                pass
            elif page["markdown"].startswith("### Step 2/5"):
                project_description = extract_section_content(
                    page["markdown"], "#### Project Description"
                )
                key_components = extract_code(
                    extract_section_content(page["markdown"], "#### Key Components")
                )
                if key_components:
                    key_components = json.loads(key_components)
                else:
                    key_components = []
                updated_step_attributes = {
                    "refined_description": project_description,
                    "key_components": key_components,
                }
                project_meta = get_project_metadata_for_page(page["id"])
                self.agents_queue.enqueue(
                    "agents.wikiagent.project_agent.utils.update_tape_step",
                    kwargs={
                        "wiki_context": WikiContextInfo(
                            page_id=page["id"],
                            project_id=project_meta["project_id"],
                            project_context=ProjectContextInfo(
                                tapes_chapter_id=project_meta["tapes"]["chapter_id"]
                            ),
                        ),
                        "step_index": -1,
                        "update": updated_step_attributes,
                    },
                )

            elif page["markdown"].startswith("### Step 3/5"):
                simple = extract_code(
                    extract_section_content(page["markdown"], "##### Simple")
                )
                if simple:
                    simple = json.loads(simple)
                detailed = extract_code(
                    extract_section_content(page["markdown"], "##### Detailed")
                )
                if detailed:
                    detailed = json.loads(detailed)
                updated_step_attributes = {
                    "simple_structure": simple,
                    "detailed_structure": detailed,
                }
                project_meta = get_project_metadata_for_page(page["id"])
                self.agents_queue.enqueue(
                    "agents.wikiagent.project_agent.utils.update_tape_step",
                    kwargs={
                        "wiki_context": WikiContextInfo(
                            page_id=page["id"],
                            project_id=project_meta["project_id"],
                            project_context=ProjectContextInfo(
                                tapes_chapter_id=project_meta["tapes"]["chapter_id"]
                            ),
                        ),
                        "step_index": -1,
                        "update": updated_step_attributes,
                    },
                )
            elif page["markdown"].startswith("### Step 4/5"):
                agent_instances = extract_code(
                    extract_section_content(page["markdown"], "#### Agent Instances")
                )
                if agent_instances:
                    agent_instances = json.loads(agent_instances)
                updated_step_attributes = {
                    "agent_instances": agent_instances,
                }
                project_meta = get_project_metadata_for_page(page["id"])
                self.agents_queue.enqueue(
                    "agents.wikiagent.project_agent.utils.update_tape_step",
                    kwargs={
                        "wiki_context": WikiContextInfo(
                            page_id=page["id"],
                            project_id=project_meta["project_id"],
                            project_context=ProjectContextInfo(
                                tapes_chapter_id=project_meta["tapes"]["chapter_id"]
                            ),
                        ),
                        "step_index": -1,
                        "update": updated_step_attributes,
                    },
                )
            elif page["markdown"].startswith("### Step 5/5"):
                pages = extract_code(
                    extract_section_content(
                        page["markdown"],
                        "#### Page Generation Instructions & Agent Assignment",
                    )
                )
                if pages:
                    pages = json.loads(pages)
                updated_step_attributes = {
                    "pages": pages,
                }
                project_meta = get_project_metadata_for_page(page["id"])
                self.agents_queue.enqueue(
                    "agents.wikiagent.project_agent.utils.update_tape_step",
                    kwargs={
                        "wiki_context": WikiContextInfo(
                            page_id=page["id"],
                            project_id=project_meta["project_id"],
                            project_context=ProjectContextInfo(
                                tapes_chapter_id=project_meta["tapes"]["chapter_id"]
                            ),
                        ),
                        "step_index": -1,
                        "update": updated_step_attributes,
                    },
                )

    def handle_page_delete(self, event: BookStackWebhookPayload):
        if event.related_item.book_id in [
            CONTENT_TASK_AGENTS_BOOK_ID,
            CREATIVE_FEEDBACK_GROUPS_BOOK_ID,
            CONTENT_INTEGRITY_AGENTS_BOOK_ID,
        ]:
            AgentOnboarding().offboard_agent(event.related_item.name)
        elif event.related_item.book_id == TOOLS_BOOK_ID:
            ToolsRedisCache().delete_tool(event.related_item.name)
            # TODO maybe delete ref in agents

    def is_agent_page(self, page: dict):
        return "Agent" in [t["name"] for t in page["tags"]]
