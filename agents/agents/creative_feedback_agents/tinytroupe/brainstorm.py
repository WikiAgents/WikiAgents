import json
import re
from typing import List, Optional

import tinytroupe
from agents.base import WikiAgentBase
from agents.steps import CommentResponse
from bs4 import BeautifulSoup
from tinytroupe.agent import TinyPerson
from tinytroupe.control import transactional
from tinytroupe.environment import TinySocialNetwork, TinyWorld

from shared.agents_redis_cache import AgentsRedisCache
from shared.bookstack_client import AgentBookStackClient
from shared.models import RedisAgent, WikiContextInfo
from shared.utils import get_project_metadata_for_page

BRAINSTORM_PROMPT = """Alright folks, let's all focus on the document and brainstorm about it.
Here is the document:
                    
{page_content}

DOCUMENT END

When you talk, use HTML styling tags to make a structured response. The following tags are supported: <strong>, <i>, <li>, <ul>. DO NOT USE <br> in the beginning of your output!
You are encouraged to use emojis when appropriate.
Start with the brainstorming now.
"""

SUMMARY_PROMPT = "Can you please consolidate the ideas that the group came up with? Provide a lot of details on each idea, and complement anything missing."


def extract_rounds(comment: str):
    pattern = r"(\d+)\s+rounds"
    match = re.search(pattern, comment)
    if match:
        n = int(match.group(1))
        updated_comment = re.sub(pattern, "", comment)
        return updated_comment, n
    return comment, None


class TinyWikiWorld(TinyWorld):
    def set_wiki_context(self, page_id: int, comment_id: Optional[int] = None):
        self.page_id = page_id
        self.comment_id = comment_id

    @transactional
    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        super()._handle_talk(source_agent=source_agent, content=content, target=target)
        client = AgentBookStackClient(source_agent.name)
        client.create_comment(content, page_id=self.page_id, parent_id=self.comment_id)


class TinyTroupeBrainstorming(WikiAgentBase):
    def react_to_command(
        agent_contexts: List[RedisAgent] | List[dict],
        wiki_context: WikiContextInfo | dict,
        comment: str,
    ) -> List[CommentResponse]:
        if isinstance(agent_contexts[0], dict):
            agent_contexts = [
                RedisAgent(**agent_context) for agent_context in agent_contexts
            ]
        if isinstance(wiki_context, dict):
            wiki_context = WikiContextInfo(**wiki_context)
        comment, n_rounds = extract_rounds(comment)
        if n_rounds is None:
            n_rounds = 2
        agents = [
            TinyPerson.load_spec(a.parameters["tiny_dump"])
            for a in agent_contexts
            if a.parameters and "tiny_dump" in a.parameters
        ]
        if len(agents) == 0:
            return [
                CommentResponse(
                    agent_name="WikiAgent", comment="💥 No TinyTroupe Agents found!"
                )
            ]
        client = AgentBookStackClient("WikiAgent")
        page_content = client.get_page(wiki_context.page_id)
        goal = comment
        if comment.startswith("/"):
            split = comment.split(" ", 1)
            if len(split) == 2:
                goal = split[1]
        world = TinyWikiWorld("Focus group", agents)
        world.communication_display = False
        world.set_wiki_context(
            page_id=wiki_context.page_id, comment_id=wiki_context.local_comment_id
        )
        world.make_everyone_accessible()
        world.broadcast(BRAINSTORM_PROMPT.format(page_content=page_content))
        if goal:
            world.broadcast_internal_goal(goal)
        r = world.run(n_rounds, return_actions=True)
        rapporteur = world.get_agent_by_name(agents[0].name)
        summary = rapporteur.listen_and_act(SUMMARY_PROMPT, return_actions=True)
        talks = [
            t["action"]["content"] for t in summary if t["action"]["type"] == "TALK"
        ]
        if len(talks) == 0:
            return [
                CommentResponse(
                    agent_name=agents[0].name,
                    comment="Everyone's so deep in thought, they forgot to come back with answers! Try to refine the goal.",
                )
            ]
        return [CommentResponse(agent_name=agents[0].name, comment=t) for t in talks]
