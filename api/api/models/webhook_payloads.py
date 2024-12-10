from typing import Optional, Union

from pydantic import BaseModel


class BookStackRelatedItem(BaseModel):
    id: int
    book_id: Optional[int] = None
    chapter_id: Optional[int] = None
    name: str
    slug: str
    priority: int = 0
    created_at: str
    updated_at: str
    created_by: dict
    updated_by: dict
    draft: bool = False
    revision_count: int = 0
    template: bool = False
    owned_by: dict
    current_revision: Optional[dict] = None


class BookStackRelatedComment(BaseModel):
    created: str
    created_at: str
    created_by: int
    entity_id: int
    entity_type: str
    html: str
    id: int
    local_id: int
    parent_id: Optional[int] = None
    updated: str
    updated_at: str
    updated_by: int


class BookStackWebhookPayload(BaseModel):

    event: str
    text: str
    triggered_at: str
    triggered_by: dict
    triggered_by_profile_url: str
    webhook_id: int
    webhook_name: str
    url: Optional[str] = None
    related_item: Optional[Union[BookStackRelatedItem, BookStackRelatedComment]] = None
