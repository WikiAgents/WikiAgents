from typing import Optional

from redis import Redis
from rq import Queue

from shared.models import WikiContextInfo


def check_bias(wiki_context: dict, comment: str):
    """Use this tool to check if the provided content is biased.

    Args:
        wiki_context (dict): The wiki context dict. Must not contain the root "wiki_context" key!
        comment (str): The users comment

    Returns:
        str: The detected biases

    """
    queue = Queue("agents-queue", Redis("redis", 6379), is_async=False)
    job = queue.enqueue(
        "agents.content_integrity.bias.bias_scanner.bias_scanner.run_bias_scanner_agent",
        timeout=600,
        kwargs={"wiki_context": wiki_context, "comment": comment},
    )
    return job.result
