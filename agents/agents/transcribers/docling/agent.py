from typing import List, Optional

from agents.base import WikiAgentBase
from agents.steps import CommentResponse
from docling.document_converter import DocumentConverter

from shared.bookstack_client import AgentBookStackClient
from shared.models import RedisAgent, WikiContextInfo


class DoclingTranscriber(WikiAgentBase):
    @staticmethod
    def react_to_command(
        agent_contexts: List[RedisAgent] | List[dict],
        wiki_context: WikiContextInfo | dict,
        comment: str,
    ) -> List[CommentResponse]:
        if isinstance(wiki_context, dict):
            wiki_context = WikiContextInfo(**wiki_context)

        client = AgentBookStackClient("WikiAgent")
        attachments = client.get_attachments(wiki_context.page_id)
        if len(attachments) == 0:
            return [
                CommentResponse(
                    agent_name="WikiAgent",
                    comment="💥 Nothing to transcribe! Add an attachment to the page.",
                )
            ]
        elif len(attachments) == 1:
            attachment = client.get_attachment(attachments[0]["id"])
            converter = DocumentConverter()
            result = converter.convert(attachment["content"])
            markdown = result.document.export_to_markdown()
            client.update_page(wiki_context.page_id, markdown=markdown)
        else:
            pass
        return [
            CommentResponse(agent_name="WikiAgent", comment="🚀 Attachment transcribed!")
        ]
