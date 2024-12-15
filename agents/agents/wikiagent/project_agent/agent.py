import logging

logging.basicConfig(level=logging.DEBUG)
import json
from typing import Any

from agents.wikiagent.project_agent.environment import ProjectPlannerEnvironment
from agents.wikiagent.project_agent.prompts import PromptRegistry
from agents.wikiagent.project_agent.steps import (
    AgentSelectionThought,
    OutputStructureSuggestionThought,
    ProjectMetadata,
    ProjectPlannerAgentStep,
    RefineProjectRequirementsThought,
    agent_selection_steps,
    output_structure_suggestion_steps,
    project_requirements_refinement_steps,
    agent_selection_plan_steps,
    ProjectPlannerAgentTapeStep,
    FinalRefineProjectRequirementsThought,
)
from agents.wikiagent.project_agent.tape import ProjectPlannerTape
from pydantic import Field
from tapeagents.agent import Agent, Node
from tapeagents.core import Observation, Prompt, SetNextNode, Step, StopStep, Tape
from tapeagents.dialog_tape import (
    AssistantStep,
    AssistantThought,
    DialogContext,
    DialogStep,
    DialogTape,
    FunctionCall,
    ToolCall,
    ToolCalls,
    UserStep,
)
from tapeagents.environment import ToolEnvironment
from tapeagents.llms import LLM, LiteLLM, LLMStream
from tapeagents.nodes import ControlFlowNode, MonoNode
from tapeagents.orchestrator import main_loop
from tapeagents.prompting import tape_to_messages
from tools.wikiagents.bias_checker import check_bias
from tools.wikiagents.creative_feedback import get_creative_feedback
from tools.wikiagents.fact_checker import fact_checker
from tools.wikiagents.generic_rq_tool_wrapper import call_rq_function

from shared.bookstack_client import AgentBookStackClient

# from shared.constants import *

from shared.models import ProjectContextInfo, WikiContextInfo
from agents.base.nodes import WikiAgentsMonoNode

from agents.wikiagent.project_agent.utils import (
    get_project_requirements_tape,
    save_project_requirements_tape,
)

from shared.utils import extract_section_content, extract_code
from agents.wikiagent.project_agent.wizard_content import *
from shared.agents_redis_cache import AgentsRedisCache, RedisAgent

from agents.creative_feedback_agents.tinytroupe.brainstorm import (
    TinyTroupeBrainstorming,
)
from agents.creative_feedback_agents.tinytroupe.project_brainstorming import (
    project_requirements_brainstorming,
)


llm = LiteLLM(
    # base_url="http://host.docker.internal:8000/v1",
    # model_name="openai/Hermes-3-Llama-3.1-8B-Q6_K_L.gguf"
    model_name="gpt-4o-mini-2024-07-18"
)


class ProjectPlannerNode(WikiAgentsMonoNode[ProjectPlannerTape]):
    system_prompt: str = PromptRegistry.system_prompt
    steps_prompt: str = PromptRegistry.allowed_steps
    allowed_steps: str
    agent_step_cls: Any = Field(exclude=True, default=ProjectPlannerAgentStep)


class ProjectRequirementsWizard:
    def __init__(self, wiki_context: WikiContextInfo, comment: str):
        self.wiki_context = wiki_context
        self.comment = comment
        self.client = AgentBookStackClient("WikiAgent")
        self.page = self.client.get_page(wiki_context.page_id)
        self.page_content = self.page["markdown"]
        self.env = ProjectPlannerEnvironment("WikiAgent")
        self.next_steps: dict = {
            "### Step 1/4": self.refine_project_requirements,
            "### Step 2/4": self.suggest_output_structure,
            "### Step 3/4": self.suggest_agents,
            "### Step 4/4": lambda: None,
        }

    def run_next_step(self):
        self.current_step = self.page_content.split("\n", 1)[0].strip()
        return self.next_steps[self.current_step]()

    def refine_project_requirements(self):
        project_description = extract_section_content(
            self.page_content, "#### Project Description"
        )
        project_type = extract_section_content(self.page_content, "#### Project Type")
        creative_agents_config = extract_code(
            extract_section_content(self.page_content, "#### Creative Feedback Agents")
        )

        grounding_config = extract_code(
            extract_section_content(self.page_content, "#### Grounding")
        )
        if grounding_config:
            grounding_config = json.loads(grounding_config)

        if creative_agents_config:
            creative_agents_config = json.loads(creative_agents_config)
            redis = AgentsRedisCache()
            creative_agents = [
                redis.get_agent(a) for a in creative_agents_config.get("agents", [])
            ]
            n_rounds = creative_agents_config.get("rounds", 3)
            agents_str = (
                ", ".join([a.name for a in creative_agents[:-1]])
                + " and "
                + creative_agents[-1].name
            )
            comment_id = self.client.create_comment(
                f"🚀<strong>{agents_str}</strong> will brainstorm about your project! I will use the summary of their discussion for the project refinement.",
                page_id=self.wiki_context.page_id,
            )
            comments = project_requirements_brainstorming(
                agent_contexts=creative_agents,
                wiki_context=WikiContextInfo(
                    page_id=self.wiki_context.page_id, local_comment_id=comment_id
                ),
                project_description=project_description,
                project_type=project_type,
                rounds=n_rounds,
            )
            brainstorming_summary = comments[0].comment
            self.client.create_comment(
                brainstorming_summary,
                page_id=self.wiki_context.page_id,
                parent_id=comment_id,
            )

        tape = ProjectPlannerTape(
            steps=[
                ProjectMetadata(
                    name=self.wiki_context.project_name,
                    project_id=self.wiki_context.project_id,
                    type=project_type,
                    initial_project_description=project_description,
                )
            ]
        )
        nodes = [
            ProjectPlannerNode(
                name="requirements_refinement",
                guidance=PromptRegistry.project_requirements_refinement,
                allowed_steps=project_requirements_refinement_steps,
                next_node="final_requirements_refinement",
            )
        ]
        if creative_agents_config:
            nodes.append(
                ProjectPlannerNode(
                    name="brainstorming_result_incorporation",
                    guidance=PromptRegistry.brainstorming_incorporation.format(
                        brainstorming_summary=brainstorming_summary
                    ),
                    allowed_steps=project_requirements_refinement_steps,
                    next_node="final_requirements_refinement",
                )
            )
            nodes[0].next_node = "brainstorming_result_incorporation"
        nodes.append(
            ProjectPlannerNode(
                name="final_requirements_refinement",
                guidance=PromptRegistry.final_requirements_refinement,
                allowed_steps=project_requirements_refinement_steps,
                next_node="final_requirements_refinement",
            )
        )
        agent = Agent.create(
            llm,
            nodes=nodes,
        )
        for event in main_loop(agent, tape, self.env):
            if ae := event.agent_event:
                if isinstance(ae.step, FinalRefineProjectRequirementsThought):
                    tape = ae.partial_tape
                    break
        assert isinstance(tape[-1], FinalRefineProjectRequirementsThought)
        key_components = "\n".join(f"- {item}" for item in tape[-1].key_components)
        new_content = STEP_2.format(
            project_description=tape[-1].refined_description,
            key_components=key_components,
        )
        self.client.update_page(page_id=self.page["id"], markdown=new_content)

        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_2_COMMENT

    def suggest_output_structure(self):
        tape = get_project_requirements_tape(wiki_context=self.wiki_context)
        if tape is None:
            return "💥 Tape not found!"
        tape = tape.append(SetNextNode(next_node="output_structure_planner"))
        agent = Agent.create(
            llm,
            nodes=[
                ProjectPlannerNode(
                    name="output_structure_planner",
                    guidance=PromptRegistry.output_structure_suggestion,
                    allowed_steps=output_structure_suggestion_steps,
                    next_node="output_structure_planner",
                )
            ],
        )
        for event in main_loop(agent, tape, self.env):
            if ae := event.agent_event:
                if isinstance(ae.step, OutputStructureSuggestionThought):
                    tape = ae.partial_tape
                    break
        assert isinstance(tape[-1], OutputStructureSuggestionThought)
        simple_structure = (
            f"```json\n{json.dumps(tape[-1].simple_structure, indent=2)}\n```"
        )
        detailed_structure = (
            f"```json\n{json.dumps(tape[-1].detailed_structure, indent=2)}\n```"
        )
        new_content = STEP_3.format(
            simple_structure=simple_structure, detailed_structure=detailed_structure
        )
        self.client.update_page(page_id=self.page["id"], markdown=new_content)
        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_3_COMMENT

    def suggest_agents(self):
        tape = get_project_requirements_tape(wiki_context=self.wiki_context)
        if tape is None:
            return "💥 Tape not found!"
        structure_type = self.comment.split(" ", 1)[-1].strip()
        if structure_type not in ["simple", "detailed"]:
            return "💥 Invalid command! Try <b>/next simple</b> or <b>/next detailed</b>"
        # TODO remove other structure from tape?
        tape = tape.append(
            UserStep(content=f"The user has selected the {structure_type} structure.")
        )
        tape = tape.append(SetNextNode(next_node="agents_selector"))
        agent = Agent.create(
            llm,
            nodes=[
                ProjectPlannerNode(
                    name="agents_selector_plan",
                    system_prompt=PromptRegistry.select_agents,
                    guidance="Follow the plan.",
                    allowed_steps=agent_selection_plan_steps,
                    next_node="agents_selector",
                ),
                ProjectPlannerNode(
                    name="agents_selector",
                    system_prompt=PromptRegistry.select_agents,
                    guidance=PromptRegistry.select_agents,
                    allowed_steps=agent_selection_steps,
                    next_node="agents_selector",
                ),
            ],
        )
        for event in main_loop(agent, tape, self.env):
            if ae := event.agent_event:
                if isinstance(ae.step, AgentSelectionThought):
                    tape = ae.partial_tape
                    break
        assert isinstance(tape[-1], AgentSelectionThought)
        selected_agents = (
            f"```json\n{json.dumps(tape[-1].selected_agents, indent=2)}\n```"
        )
        new_content = STEP_4.format(selected_agents=selected_agents)
        self.client.update_page(page_id=self.page["id"], markdown=new_content)
        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_4_COMMENT


def react_to_comment(wiki_context: WikiContextInfo, comment: str):
    comment_response = None
    if comment.startswith("/next"):
        comment_response = ProjectRequirementsWizard(
            wiki_context, comment
        ).run_next_step()

    if comment_response and len(comment_response) > 0:
        AgentBookStackClient("WikiAgent").create_comment(
            comment_response,
            page_id=wiki_context.page_id,
            parent_id=wiki_context.local_comment_id,
        )
