from typing import Annotated, List, Literal, Optional, TypeAlias, Union

from pydantic import Field
from tapeagents.core import (
    Observation,
)
from tapeagents.utils import get_step_schemas_from_union_type

from agents.base.steps import (
    WikiAgentsTapeStep,
    WikiAgentsThought,
    WikiAgentsObservation,
    WikiAgentsAction,
)


class ProjectMetadata(Observation):
    kind: Literal["project_metadata"] = "project_metadata"
    project_id: int = Field(description="The id of the project")
    name: str = Field(description="The name of the project")
    type: str = Field(
        description="The type of the project. E.g. Topic Compendium, Research, Code"
    )
    initial_project_description: str = Field(
        description="The initial project description provided by the user."
    )


class RefineProjectRequirementsThought(WikiAgentsThought):
    kind: Literal["project_requirements_refinement"] = "project_requirements_refinement"
    key_components: List[str] = Field(
        description="The key components and subtopics of the project."
    )
    refined_description: str = Field(
        description="A refined version of the users' initial project description"
    )


class FinalRefineProjectRequirementsThought(WikiAgentsThought):
    kind: Literal["final_requirements_refinement"] = "final_requirements_refinement"
    key_components: List[str] = Field(
        description="The key components and subtopics of the project. Must be high quality!"
    )
    refined_description: str = Field(
        description="The final version of the project description. Must be high quality!"
    )


class OutputStructureSuggestionThought(WikiAgentsThought):
    kind: Literal[
        "project_output_structure_suggestion"
    ] = "project_output_structure_suggestion"
    simple_structure: dict = Field(
        description="The suggested, simple output structure for this project."
    )
    detailed_structure: dict = Field(
        description="The suggested, detailed output structure for this project."
    )


class GetAvailableAgentsAction(WikiAgentsAction):
    """
    Action that returns all available agents.
    """

    kind: Literal["get_available_agents"] = "get_available_agents"


class AvailableAgentsObservation(WikiAgentsObservation):
    kind: Literal["available_agents_observation"] = "available_agents_observation"
    agents: List[dict]


class AgentSelectionThought(WikiAgentsThought):
    kind: Literal["agent_selection_thought"] = "agent_selection_thought"
    selected_agents: List[dict] = Field(
        description="The list of selected agents. Must be in the form of: [{'name': <agent_name>, 'agent_id': <agent_page_id>, 'reason': <why_the_agent_was_chosen>}]"
    )


class GetTools(WikiAgentsAction):
    """
    Action that returns all available tools.
    """

    kind: Literal["get_all_tools"] = "get_all_tools"


class AllToolsObservation(WikiAgentsObservation):
    kind: Literal["all_tools_observation"] = "all_tools_observation"
    tools: List[dict]


class AgentInstancesThought(WikiAgentsThought):
    kind: Literal["agent_instances_thought"] = "agent_instances_thought"
    agent_instances: List[dict] = Field(
        description="The list of agent instances. Must be in the form of: [{'name': <unique_agent_name>, 'agent_id': <agent_page_id>, 'description': <agent_description>, 'parameters': <customized_parameters>, 'tools': <list_of_tool_names>}]"
    )


ProjectPlannerAgentTapeStep = (
    Union[
        ProjectMetadata,
        RefineProjectRequirementsThought,
        FinalRefineProjectRequirementsThought,
        OutputStructureSuggestionThought,
        GetAvailableAgentsAction,
        AvailableAgentsObservation,
        AgentSelectionThought,
        GetTools,
        AllToolsObservation,
        AgentInstancesThought,
    ]
    | WikiAgentsTapeStep
)


ProjectPlannerAgentStep: TypeAlias = Annotated[
    ProjectPlannerAgentTapeStep,
    Field(discriminator="kind"),
]


project_requirements_refinement_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[RefineProjectRequirementsThought, FinalRefineProjectRequirementsThought],
        Field(discriminator="kind"),
    ]
)

output_structure_suggestion_steps = get_step_schemas_from_union_type(
    Annotated[Union[OutputStructureSuggestionThought], Field(discriminator="kind")]
)


agent_selection_plan_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[GetAvailableAgentsAction, AvailableAgentsObservation],
        Field(discriminator="kind"),
    ]
)


agent_selection_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[
            AgentSelectionThought, GetTools, AllToolsObservation, AgentInstancesThought
        ],
        Field(discriminator="kind"),
    ]
)
