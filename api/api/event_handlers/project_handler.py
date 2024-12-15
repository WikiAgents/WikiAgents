from api.event_handlers.base_handler import BaseEventHandler
from api.models.webhook_payloads import BookStackRelatedItem, BookStackWebhookPayload
from shared.constants import *
from shared.agents_redis_cache import AgentsRedisCache
import json


class ProjectEventHandler(BaseEventHandler):
    def handle_project_create(self, event: BookStackWebhookPayload):
        project = self.client.get_shelf(event.related_item.id)
        description = project["description"]
        metadata_book = self.client.create_book(
            PROJECT_METADATA_BOOK_NAME, description=PROJECT_METADATA_BOOK_DESCRIPTION
        )
        self.client.update_shelf(project["id"], books=[metadata_book["id"]])
        creative_agents = AgentsRedisCache().get_agents_by_type("creative_agent")
        creative_agents = [a.name for a in creative_agents]
        configured_creatives = {"agents": [], "rounds": 3}
        grounding = {
            "agent": "Prompt Grounder",
            "grounding": ["<knowledge_base_book>/<knowledge_base_page>"],
        }
        requirements_page = self.client.create_page(
            metadata_book["id"],
            name=PROJECT_REQUIREMENTS_PAGE_NAME,
            markdown=PROJECT_REQUIREMENTS_STEP_1.format(
                project_description=description,
                configured_creatives=f"```json\n{json.dumps(configured_creatives, indent=2)}\n```",
                available_creatives=f"```json\n{json.dumps(creative_agents)}\n```",
                grounding=f"```json\n{json.dumps(grounding, indent=2)}\n```",
            ),
            tags=[{"name": "WikiAgents", "value": "Requirements"}],
        )
        involved_agents_chapter = self.client.create_chapter(
            metadata_book["id"],
            name=PROJECT_AGENTS_CHAPTER_NAME,
            description=PROJECT_AGENTS_CHAPTER_DESCRIPTION,
        )
        creative_feedback_groups_chapter = self.client.create_chapter(
            metadata_book["id"],
            name=PROJECT_CREATIVE_FEEDBACK_CHAPTER_NAME,
            description=PROJECT_CREATIVE_FEEDBACK_CHAPTER_DESCRIPTION,
        )
        factual_feedback_groups_chapter = self.client.create_chapter(
            metadata_book["id"],
            name=PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_NAME,
            description=PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_DESCRIPTION,
        )
        tapes_chapter = self.client.create_chapter(
            metadata_book["id"],
            name=PROJECT_TAPES_CHAPTER_NAME,
            description=PROJECT_TAPES_CHAPTER_DESCRIPTION,
        )
        requirements_tape_page = self.client.create_page(
            metadata_book["id"],
            chapter_id=tapes_chapter["id"],
            name=PROJECT_REQUIREMENTS_TAPE_PAGE_NAME,
            markdown="*This page will contain the tape of the project requirements analysis step.*",
            tags=[
                {"name": "WikiAgents", "value": "Requirements"},
                {"name": "WikiAgents", "value": "Tape"},
            ],
        )

    def handle_project_update(self, event: BookStackWebhookPayload):
        pass

    def handle_project_delete(self, event: BookStackWebhookPayload):
        pass
