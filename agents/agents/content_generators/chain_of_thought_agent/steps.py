from tapeagents.utils import get_step_schemas_from_union_type
from typing import Annotated, List, Literal, Optional, TypeAlias, Union
from pydantic import Field

from agents.base.steps import (
    WikiAgentsTapeStep,
    WikiAgentsThought,
    WikiAgentsObservation,
    WikiAgentsAction,
    WikiAgentsStep,
    ReadPageAction,
    ReadPageObservation,
    UserDefinedTool,
    UserDefinedToolObservation,
    AssistantStep,
)


class PlanThought(WikiAgentsThought):
    kind: Literal["plan"] = "plan"
    plan: List[str] = Field(description="The list containing each planned step.")


ChainOfThoughtAgentTapeStep = (
    Union[
        PlanThought,
    ]
    | WikiAgentsTapeStep
)


ChainOfThoughtAgentStep: TypeAlias = Annotated[
    ChainOfThoughtAgentTapeStep,
    Field(discriminator="kind"),
]


plan_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[PlanThought],
        Field(discriminator="kind"),
    ]
)

act_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[
            # ReadPageAction,
            # ReadPageObservation,
            UserDefinedTool,
            UserDefinedToolObservation,
            AssistantStep,
        ],
        Field(discriminator="kind"),
    ]
)
