from api.event_handlers.base_handler import BaseEventHandler
from api.models.webhook_payloads import BookStackWebhookPayload
from shared.agent_onboarding import AgentOnboarding

# from shared.agent_onboarding import generate_agent_user, set_agent_details, offboard_agent
from shared.models import AgentType, RedisAgent

CONTENT_TASK_AGENTS_BOOK_ID = 1
CREATIVE_FEEDBACK_GROUPS_BOOK_ID = 3
CONTENT_INTEGRITY_AGENTS_BOOK_ID = 4


class PageEventHandler(BaseEventHandler):
    def handle_page_create(self, event: BookStackWebhookPayload):
        page = self.client.get_page(event.related_item.id)
        if event.related_item.book_id == CONTENT_TASK_AGENTS_BOOK_ID:
            AgentOnboarding().onboard_agent(
                RedisAgent(
                    type="content_agent",
                    name=page["name"],
                    page_id=page["id"],
                )
            )

        elif event.related_item.book_id == CREATIVE_FEEDBACK_GROUPS_BOOK_ID:
            if page["chapter_id"] > 0:
                self.agents_queue.enqueue(
                    "agents.creative_feedback_agents.tinytroupe.personas.create_persona",
                    kwargs={"page_id": page["id"], "chapter_id": page["chapter_id"]},
                )

        elif event.related_item.book_id == CONTENT_INTEGRITY_AGENTS_BOOK_ID:
            pass

    def handle_page_update(self, event: BookStackWebhookPayload):
        pass  # TODO sync agent redis

    def handle_page_delete(self, event: BookStackWebhookPayload):
        if event.related_item.book_id in [
            CONTENT_TASK_AGENTS_BOOK_ID,
            CREATIVE_FEEDBACK_GROUPS_BOOK_ID,
            CONTENT_INTEGRITY_AGENTS_BOOK_ID,
        ]:
            AgentOnboarding().offboard_agent(event.related_item.name)

    def is_agent_page(self, page: dict):
        return "Agent" in [t["name"] for t in page["tags"]]
