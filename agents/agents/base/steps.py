from typing import Annotated, List, Literal, Optional, TypeAlias, Union

from pydantic import BaseModel, Field
from tapeagents.core import (
    Action,
    Error,
    LLMOutputParsingFailureAction,
    Observation,
    SetNextNode,
    StopStep,
    Thought,
)
from tapeagents.dialog_tape import AssistantStep, UserStep
from tapeagents.utils import get_step_schemas_from_union_type


class WikiAgentsThought(Thought):
    pass


class WikiAgentsAction(Action):
    pass


class WikiAgentsObservation(Observation):
    pass


class CommentResponse(WikiAgentsObservation):
    kind: Literal["comment_response"] = "comment_response"
    agent_name: str
    comment: str


# Book actions


class CreateBookAction(WikiAgentsAction):
    """
    Action that creates a new book.
    """

    kind: Literal["create_book_action"] = "create_book_action"
    name: str = Field(description="The name of the book to create.")
    description: str = Field(description="The description of the book.")
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class ReadBookAction(WikiAgentsAction):
    """
    Action that retrieves an overview of a book.
    """

    kind: Literal["read_book_action"] = "read_book_action"
    book_id: int = Field(description="The id of the book to read.")


class UpdateBookAction(WikiAgentsAction):
    """
    Action that updates the description and/or the tags of a book.
    """

    kind: Literal["update_book_action"] = "update_book_action"
    book_id: int = Field(description="The id of the book to update.")
    description: str = Field(description="The new description of the book.")
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class DeleteBookAction(WikiAgentsAction):
    """
    Action that deletes a book.
    """

    kind: Literal["delete_book_action"] = "delete_book_action"
    book_id: int = Field(description="The id of the book to delete.")


# Book observations


class BookOverviewObservation(WikiAgentsObservation):
    kind: Literal["book_overview_observation"] = "book_overview_observation"
    chapters: List[dict]
    pages: List[dict]


class CreateBookObservation(WikiAgentsObservation):
    kind: Literal["create_book_observation"] = "create_book_observation"
    book_id: str


class UpdateBookObservation(WikiAgentsObservation):
    kind: Literal["update_book_observation"] = "update_book_observation"
    content: str


class DeleteBookObservation(WikiAgentsObservation):
    kind: Literal["delete_book_observation"] = "delete_book_observation"
    content: str


# Chapter actions


class CreateChapterAction(WikiAgentsAction):
    """
    Action that creates a new chapter.
    """

    kind: Literal["create_chapter_action"] = "create_chapter_action"
    book_id: int = Field(description="The id of the book this chapter belongs to.")
    name: str = Field(description="The name of the chapter to create.")
    description: str = Field(description="The description of the chapter.")
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class ReadChapterAction(WikiAgentsAction):
    """
    Action that retrieves an overview of a chapter.
    """

    kind: Literal["read_chapter_action"] = "read_chapter_action"
    chapter_id: int = Field(description="The id of the chapter to read.")


class UpdateChapterDescriptionAction(WikiAgentsAction):
    """
    Action that updates the description of a chapter.
    """

    kind: Literal["update_chapter_action"] = "update_chapter_action"
    chapter_id: int = Field(description="The id of the chapter to update.")
    description: str = Field(description="The new description of the chapter.")
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class DeleteChapterAction(WikiAgentsAction):
    """
    Action that deletes an entire chapter. All included pages will be deleted aswell!
    """

    kind: Literal["delete_chapter_action"] = "delete_chapter_action"
    chapter_id: int = Field(description="The id of the chapter to delete.")


# Chapter observations


class ChapterOverviewObservation(WikiAgentsObservation):
    kind: Literal["chapter_overview_observation"] = "chapter_overview_observation"
    name: str
    description: str
    pages: List[dict]
    tags: List[dict]


class CreateChapterObservation(WikiAgentsObservation):
    kind: Literal["create_chapter_observation"] = "create_chapter_observation"
    chapter_id: str


class UpdateChapterObservation(WikiAgentsObservation):
    kind: Literal["update_chapter_observation"] = "update_chapter_observation"
    content: str


class DeleteChapterObservation(WikiAgentsObservation):
    kind: Literal["delete_chapter_observation"] = "delete_chapter_observation"
    content: str


# Page actions


class CreatePageAction(WikiAgentsAction):
    """
    Action that creates a new page.
    """

    kind: Literal["create_page_action"] = "create_page_action"
    name: str = Field(description="The name of the page to create.")
    content: str = Field(description="The markdown content of the page.")
    book_id: int = Field(description="The id of the book this page belongs to.")
    chapter_id: Optional[int] = Field(
        default=0,
        description="The id of the chapter this page belongs to, if applicable.",
    )
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class ReadPageAction(WikiAgentsAction):
    """
    Action that retrieves the content of a page.
    """

    kind: Literal["read_page_action"] = "read_page_action"
    page_id: int = Field(description="The id of the page to read.")


class UpdatePageContentAction(WikiAgentsAction):
    """
    Action that updates a page.
    """

    kind: Literal["update_page_action"] = "update_page_action"
    page_id: int = Field(description="The id of the page to update.")
    name: str = Field(description="The new name of the page.")
    chapter_id: int = Field(
        description="The id of the chapter the page should belong to."
    )
    content: str = Field(description="The new markdown content of the page.")
    tags: List[dict] = Field(
        default=[],
        description="A list of tags in the form: [{'name': <tag_name>, 'value': <tag_value>}]. tag_value is optional and can be None",
    )


class DeletePageAction(WikiAgentsAction):
    """
    Action that deletes a page.
    """

    kind: Literal["delete_page_action"] = "delete_page_action"
    page_id: int = Field(description="The id of the page to delete.")


# Page observations


class ReadPageObservation(WikiAgentsObservation):
    kind: Literal["read_page_observation"] = "read_page_observation"
    content: str
    tags: List[dict]


class CreatePageObservation(WikiAgentsObservation):
    kind: Literal["create_page_observation"] = "create_page_observation"
    page_id: str


class UpdatePageObservation(WikiAgentsObservation):
    kind: Literal["update_page_observation"] = "update_page_observation"
    content: str


class DeletePageObservation(WikiAgentsObservation):
    kind: Literal["delete_page_observation"] = "delete_page_observation"
    content: str


# Comment actions


class CreateCommentAction(WikiAgentsAction):
    """
    Action that creates a comment on a page.
    """

    kind: Literal["create_comment_action"] = "create_comment_action"
    page_id: int = Field(description="The id of the page to comment on.")
    parent_comment_id: Optional[int] = Field(
        default=None, description="The id of the comment to reply to. Optional"
    )
    comment: str = Field(
        description="The comment text. Can contain simple html text formatting for bold and italic texts. lists are supported aswell. NO css, NO divs!"
    )


class ReadCommentsAction(WikiAgentsAction):
    """
    Action that reads all comments on a page.
    """

    kind: Literal["read_comments_action"] = "read_comments_action"
    page_id: int = Field(description="The id of the page to read the comments from.")


class ReadCommentReplyAction(WikiAgentsAction):
    """
    Action that reads
    """

    kind: Literal["read_comment_reply"] = "read_comment_reply"
    page_id: int = Field(description="The id of the page to read the comment from.")
    comment_id: int = Field(
        description="The id of the comment that this action reads the reply"
    )


# Comment observation


class CreateCommentObservation(WikiAgentsObservation):
    kind: Literal["create_comment_observation"] = "create_comment_observation"
    comment_id: int


class ReadCommentsObservation(WikiAgentsObservation):
    kind: Literal["read_comments_observation"] = "read_comments_observation"
    comments: List[dict]


class ReadCommentReplyObservation(WikiAgentsObservation):
    kind: Literal["read_comment_reply_observation"] = "read_comment_reply_observation"
    user_name: str
    comment_id: int
    content: str


# Errors


class ActionExecutionFailure(WikiAgentsObservation, Error):
    kind: Literal["action_execution_failure"] = "action_execution_failure"
    error: str


# User-defined Actions


class UserDefinedAction(WikiAgentsAction):
    """
    Action that calls a user-defined tool.
    """

    kind: Literal["userdefined_action"] = "userdefined_action"
    function: str = Field(description="The name of the function to call.")
    parameters: dict = Field(description="the ")


class UserDefinedActionObservation(WikiAgentsObservation):
    kind: Literal["userdefined_action_observation"] = "userdefined_action_observation"
    output: str


WikiAgentsTapeStep = Union[
    # Wiki CRUD
    CreateBookAction,
    ReadBookAction,
    UpdateBookAction,
    DeleteBookAction,
    BookOverviewObservation,
    CreateBookObservation,
    UpdateBookObservation,
    DeleteBookObservation,
    CreateChapterAction,
    ReadChapterAction,
    UpdateChapterDescriptionAction,
    DeleteChapterAction,
    ChapterOverviewObservation,
    CreateChapterObservation,
    UpdateChapterObservation,
    DeleteChapterObservation,
    CreatePageAction,
    ReadPageAction,
    UpdatePageContentAction,
    DeletePageAction,
    ReadPageObservation,
    CreatePageObservation,
    UpdatePageObservation,
    DeletePageObservation,
    CreateCommentAction,
    ReadCommentsAction,
    ReadCommentReplyAction,
    CreateCommentObservation,
    ReadCommentsObservation,
    ReadCommentReplyObservation,
    # User-defined tools
    UserDefinedAction,
    UserDefinedActionObservation,
    # Others
    LLMOutputParsingFailureAction,
    ActionExecutionFailure,
    SetNextNode,
    AssistantStep,
    UserStep,
]

WikiAgentsStep: TypeAlias = Annotated[
    WikiAgentsTapeStep,
    Field(discriminator="kind"),
]
