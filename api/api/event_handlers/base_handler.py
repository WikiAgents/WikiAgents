from redis import Redis
from rq import Queue

from shared.bookstack_client import BookStackAPIClient


class BaseEventHandler:
    def __init__(self, bookstack_client: BookStackAPIClient):
        self.client = bookstack_client
        self.agents_queue = Queue("agents-queue", Redis("redis", 6379))
