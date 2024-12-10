from typing import Optional

from shared.models import WikiContextInfo


def get_creative_feedback(wiki_context: dict, comment: str):
    """Get creative feedback or brainstorm on the content. Guide the process by setting a goal.

    Args:
        wiki_context (dict): The wiki context dict. Must not contain the root "wiki_context" key!
        comment (str): The users comment

    Returns:
        str: A summary of the discussion.

    """
    return "Brainstorming finished! This is a placeholder, act like this is a real brainstorming result."
