from typing import List, Optional

from tinytroupe.control import transactional
from tinytroupe.environment import TinySocialNetwork, TinyWorld
from tinytroupe.agent import TinyPerson
from shared.bookstack_client import AgentBookStackClient


class TinyWikiWorld(TinyWorld):
    def set_wiki_context(self, page_id: int, comment_id: Optional[int] = None):
        self.page_id = page_id
        self.comment_id = comment_id

    @transactional
    def _handle_talk(self, source_agent: TinyPerson, content: str, target: str):
        super()._handle_talk(source_agent=source_agent, content=content, target=target)
        client = AgentBookStackClient(source_agent.name)
        client.create_comment(content, page_id=self.page_id, parent_id=self.comment_id)
