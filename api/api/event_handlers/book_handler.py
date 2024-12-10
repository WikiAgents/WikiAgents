from api.event_handlers.base_handler import BaseEventHandler
from api.models.webhook_payloads import BookStackRelatedItem, BookStackWebhookPayload


class BookEventHandler(BaseEventHandler):
    def handle_book_create(self, event: BookStackWebhookPayload):
        book = self.client.get_book(event.related_item.id)
        prompt = book["description"]
        agents = [t["value"] for t in book["tags"] if t["name"] == "Agent"]
        print(prompt)
        print(agents)

    def handle_book_update(self, event: BookStackWebhookPayload):
        pass

    def handle_book_delete(self, event: BookStackWebhookPayload):
        pass
