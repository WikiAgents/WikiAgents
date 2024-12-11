from typing import List

from agents.base.steps import CommentResponse

from shared.models import RedisAgent, WikiContextInfo


class WikiAgentBase:
    """
    A class representing a content-generating agent capable of responding to comments
    and generating content based on provided parameters and contextual information.
    """

    @staticmethod
    def generate(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        instructions: str,
    ) -> str:
        """
        Generates content based on the provided wiki context, agent context and instructions.

        Args:
            agent_context (RedisAgent): Information about the agent.
            wiki_context (WikiContextInfo): Information about the origin of the event triggering this function.
            instructions (str): The instructions for the generation.

        Returns:
            str: The generated content as a string.
        """
        pass

    @staticmethod
    def react_to_comment(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        comment: str,
    ) -> List[CommentResponse]:
        """
        Reacts to a comment based on the provided wiki context and user-defined parameters.

        Args:
            agent_context (RedisAgent): Information about the agent.
            wiki_context (WikiContextInfo): Information about the origin of the event triggering this function.
            comment (str): The comment to which the agent should react.

        Returns:
            CommentResponse: The reaction to the comment.
        """
        pass

    @staticmethod
    def react_to_command(
        agent_contexts: List[RedisAgent] | List[dict],
        wiki_context: WikiContextInfo | dict,
        comment: str,
    ) -> List[CommentResponse]:
        """
        Reacts to a command comment (e.g. /check) based on the provided wiki context and user-defined parameters.

        Args:
            agent_contexts (List[RedisAgent]): Information about the agents listening to the command.
            wiki_context (WikiContextInfo): Information about the origin of the event triggering this function.
            comment (str): The comment to which the agents should react.

        Returns:
            List[CommentResponse]: The reactions to the comment.
        """
        pass
