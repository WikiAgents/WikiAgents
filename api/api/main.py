import os
from functools import wraps

from fastapi import FastAPI

from api.event_handlers.book_handler import BookEventHandler
from api.event_handlers.comment_handler import CommentEventHandler
from api.event_handlers.page_handler import PageEventHandler
from api.event_handlers.project_handler import ProjectEventHandler
from api.models.webhook_payloads import BookStackWebhookPayload
from shared.bookstack_client import BookStackAPIClient

app = FastAPI()

base_url = os.environ["APP_URL"]
token_id = os.environ["WA_TOKEN"]
token_secret = os.environ["WA_SECRET"]

bookstack_client = BookStackAPIClient(
    "http://bookstack", token_id=token_id, token_secret=token_secret
)


def check_is_agent():
    def decorator(func):
        @wraps(func)
        def wrapper(payload, *args, **kwargs):
            user_id = payload.triggered_by["id"]
            is_agent = bookstack_client.is_agent(user_id)
            if is_agent:
                print(f"Skipping function {func.__name__} for user_id: {user_id}")
                return {
                    "status": "skipped",
                    "reason": f"User {user_id} is not allowed to execute this function.",
                }
            print(f"Executing function {func.__name__} for user_id: {user_id}")
            return func(payload, *args, **kwargs)

        return wrapper

    return decorator


# Test custom bookstack endpoints


@app.get("/test")
def test():
    return "works"


# Projects


@app.post("/bookshelf_create")
def bookshelf_create(payload: BookStackWebhookPayload):
    ProjectEventHandler(bookstack_client).handle_project_create(payload)


@app.post("/bookshelf_update")
def bookshelf_update(payload: BookStackWebhookPayload):
    ProjectEventHandler(bookstack_client).handle_project_update(payload)


@app.post("/bookshelf_delete")
def bookshelf_delete(payload: BookStackWebhookPayload):
    ProjectEventHandler(bookstack_client).handle_project_delete(payload)


# Books


@app.post("/book_create")
def book_create(payload: BookStackWebhookPayload):
    BookEventHandler(bookstack_client).handle_book_create(payload)


@app.post("/book_update")
def book_update(payload: BookStackWebhookPayload):
    BookEventHandler(bookstack_client).handle_book_update(payload)


@app.post("/book_delete")
def book_delete(payload: BookStackWebhookPayload):
    BookEventHandler(bookstack_client).handle_book_delete(payload)


# Pages


@app.post("/page_create")
def page_create(payload: BookStackWebhookPayload):
    PageEventHandler(bookstack_client).handle_page_create(payload)


@app.post("/page_update")
def page_update(payload: BookStackWebhookPayload):
    PageEventHandler(bookstack_client).handle_page_update(payload)


@app.post("/page_delete")
def page_delete(payload: BookStackWebhookPayload):
    PageEventHandler(bookstack_client).handle_page_delete(payload)


# Comments


@app.post("/comment_create")
@check_is_agent()  # only respond to user comments
def comment_create(payload: BookStackWebhookPayload):
    author = payload.triggered_by["id"]
    CommentEventHandler(bookstack_client).handle_comment_create(payload)
