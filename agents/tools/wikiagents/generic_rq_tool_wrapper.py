from typing import Optional

from redis import Redis
from rq import Queue


def call_rq_function(func: str, kwargs: dict = {}):
    """Call rq functions as agent tools.

    Args:
        func (str): The path to the function
        kwargs (dict): The parameters for the function

    Returns:
        str: The result

    """
    queue = Queue("agents-queue", Redis("redis", 6379), is_async=False)
    job = queue.enqueue(func, kwargs=kwargs)
    return job.result
