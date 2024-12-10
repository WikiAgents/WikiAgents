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
