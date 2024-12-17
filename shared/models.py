from enum import Enum, auto
from typing import List, Literal, Optional

from pydantic import BaseModel


class AgentType(Enum):
    CONTENT_AGENT = "content_agent"
    CREATIVE_AGENT = "creative_agent"
    INTEGRITY_AGENT = "integrity_agent"


class ProjectContextInfo(BaseModel):
    project_id: Optional[int] = None
    metadata_book_id: Optional[int] = None
    creative_agents_chapter_id: Optional[int] = None
    integrity_agents_chapter_id: Optional[int] = None
    involved_agents_chapter_id: Optional[int] = None
    tapes_chapter_id: Optional[int] = None


class WikiContextInfo(BaseModel):
    type: Literal[
        "page_created", "comment_created", "project_created", "other"
    ] = "other"
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    book_id: Optional[int] = None
    chapter_id: Optional[int] = None
    page_id: Optional[int] = None
    page_name: Optional[str] = None
    local_comment_id: Optional[int] = None
    confirmation_comment_id: Optional[int] = None
    tape_page_id: Optional[int] = None
    tags: List[dict] = []
    project_context: Optional[ProjectContextInfo] = None


class RedisAgent(BaseModel):
    type: Optional[
        Literal[
            "content_agent",
            "content_agent_instance",
            "creative_agent",
            "integrity_agent",
            "wikiagent",
            "transcriber",
        ]
    ] = None
    name: str
    page_id: Optional[int] = None
    code_path: Optional[str] = None
    description: Optional[str] = None
    command: Optional[str] = None
    token_id: Optional[str] = None
    token_secret: Optional[str] = None
    user_id: Optional[int] = None
    parameters: Optional[dict] = None
    tools: Optional[List[str]] = None


class UserdefinedTool(BaseModel):
    name: str
    tool_id: int
    code: str
    description: Optional[str]
    function_name: Optional[str]
    parameters: Optional[dict]
