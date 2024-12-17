import logging

logging.basicConfig(level=logging.DEBUG)
import json
from typing import Any
import re

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
    AgentInstancesThought,
    page_instructions_plan_steps,
    page_instructions_steps,
    PageInstructionsThought,
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
from redis import Redis
from rq import Queue
from shared.agent_onboarding import AgentOnboarding
from shared.utils import get_project_metadata_for_page
from shared.templates import AGENT_TEMPLATE
import re


def extract_number(s: str) -> int:
    match = re.match(r"^(\d+)\.", s)
    return int(match.group(1)) if match else 1


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
            "### Step 1/5": self.refine_project_requirements,
            "### Step 2/5": self.suggest_output_structure,
            "### Step 3/5": self.suggest_agents,
            "### Step 4/5": self.page_instructions,
            "### Step 5/5": self.generate,
            "### Wizard End": lambda: None,
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

        brainstorming_summary = None
        if creative_agents_config:
            creative_agents_config = json.loads(creative_agents_config)
            if len(creative_agents_config.get("agents", [])) > 0:
                redis = AgentsRedisCache()
                creative_agents = [
                    redis.get_agent(a) for a in creative_agents_config.get("agents", [])
                ]
                focus_on = creative_agents_config.get("focus_on", "everything")
                n_rounds = creative_agents_config.get("rounds", 3)
                agents_str = (
                    ", ".join([a.name for a in creative_agents[:-1]])
                    + " and "
                    + creative_agents[-1].name
                )
                comment_id = self.client.create_comment(
                    f"🚀 <strong>{agents_str}</strong> will brainstorm about your project! I will use the summary of their discussion for the project refinement.",
                    page_id=self.page["id"],
                )
                comments = project_requirements_brainstorming(
                    agent_contexts=creative_agents,
                    wiki_context=WikiContextInfo(
                        page_id=self.page["id"], local_comment_id=comment_id
                    ),
                    project_description=project_description,
                    project_type=project_type,
                    focus_on=focus_on,
                    rounds=n_rounds,
                )
                brainstorming_summary = comments[0].comment
                self.client.create_comment(
                    brainstorming_summary,
                    page_id=self.page["id"],
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
        if brainstorming_summary:
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
        key_components = (
            f"```json\n{json.dumps(tape[-1].key_components, indent=2)}\n```"
        )
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
            UserStep(
                content=f"The user has selected the {structure_type} structure. Forget the {'simple' if structure_type == 'detailed' else 'detailed'} structure!"
            )
        )
        tape = tape.append(SetNextNode(next_node="agents_selector_plan"))
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
                    next_node="agents_selector_plan",
                ),
            ],
        )
        agent_selection_step = None
        agent_instances_step = None
        for event in main_loop(agent, tape, self.env, max_loops=10):
            if ae := event.agent_event:
                if isinstance(ae.step, AgentSelectionThought):
                    agent_selection_step = ae.step
                elif isinstance(ae.step, AgentInstancesThought):
                    tape = ae.partial_tape
                    agent_instances_step = ae.step
                    break
        assert agent_selection_step is not None
        assert agent_instances_step is not None

        selected_agents = f"```json\n{json.dumps(agent_selection_step.selected_agents, indent=2)}\n```"
        agent_instances = f"```json\n{json.dumps(agent_instances_step.agent_instances, indent=2)}\n```"
        new_content = STEP_4.format(
            selected_agents=selected_agents, agent_instances=agent_instances
        )
        self.client.update_page(page_id=self.page["id"], markdown=new_content)
        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_4_COMMENT

    def page_instructions(self):
        tape = get_project_requirements_tape(wiki_context=self.wiki_context)
        if tape is None:
            return "💥 Tape not found!"
        tape = tape.append(SetNextNode(next_node="page_instructions"))
        agents_thoughts = [
            s for s in tape.steps if isinstance(s, AgentInstancesThought)
        ]
        assert len(agents_thoughts) > 0
        agents_names = [
            {"name": a["unique_name"], "description": a["description"]}
            for a in agents_thoughts[0].agent_instances
        ]
        user_steps = [
            s
            for s in tape.steps
            if isinstance(s, UserStep)
            and s.content.startswith("The user has selected the ")
        ]
        assert len(user_steps) > 0
        match = re.search(
            r"^The user has selected the (simple|detailed)", user_steps[-1].content
        )
        assert match is not None
        output_structure_type = match.group(1)
        output_structure_steps = [
            s for s in tape.steps if isinstance(s, OutputStructureSuggestionThought)
        ]
        assert len(output_structure_steps) > 0
        if output_structure_type == "simple":
            output_structure = output_structure_steps[0].simple_structure
        else:
            output_structure = output_structure_steps[0].detailed_structure

        all_pages = []
        for book, chapters in output_structure.items():
            for chapter, pages in chapters.items():
                for page, description in pages.items():
                    all_pages.append(
                        {
                            "name": page,
                            "description": description,
                            "chapter": chapter,
                            "book": book,
                        }
                    )

        agent = Agent.create(
            llm,
            nodes=[
                # ProjectPlannerNode(
                #     name="page_instructions_plan",
                #     system_prompt=PromptRegistry.page_instructions.format(agents=agents_names, pages=pages),
                #     guidance="Follow the plan.",
                #     allowed_steps=page_instructions_plan_steps,
                #     next_node="page_instructions",
                # ),
                ProjectPlannerNode(
                    name="page_instructions",
                    system_prompt="",
                    guidance=PromptRegistry.page_instructions.format(
                        agents=agents_names, pages=all_pages
                    ),
                    allowed_steps=page_instructions_steps,
                    next_node="page_instructions",
                ),
            ],
        )
        page_instructions_step = None
        for event in main_loop(agent, tape, self.env, max_loops=5):
            if ae := event.agent_event:
                if isinstance(ae.step, PageInstructionsThought):
                    tape = ae.partial_tape
                    page_instructions_step = ae.step
                    break
        assert page_instructions_step is not None
        page_instructions = f"```json\n{json.dumps(page_instructions_step.model_dump()['pages'], indent=2)}\n```"
        new_content = STEP_5.format(page_instructions=page_instructions)
        self.client.update_page(page_id=self.page["id"], markdown=new_content)
        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_5_COMMENT

    def generate(self):
        tape = get_project_requirements_tape(wiki_context=self.wiki_context)
        if tape is None:
            return "💥 Tape not found!"

        metadata = get_project_metadata_for_page(self.page["id"])
        assert isinstance(tape[-1], PageInstructionsThought)
        # generate agent users
        agents_thoughts = [
            s for s in tape.steps if isinstance(s, AgentInstancesThought)
        ]
        assert len(agents_thoughts) > 0
        all_agents = AgentsRedisCache().get_all_agents()
        agent_instances = agents_thoughts[0].agent_instances
        for instance in agent_instances:
            base_agent = [a for a in all_agents if a.page_id == instance["page_id"]][
                0
            ].model_copy()
            base_agent.name = instance["unique_name"]
            base_agent.parameters = instance["parameters"]
            base_agent.tools = instance["tools"]
            base_agent.description = instance["description"]
            base_agent.type = "content_agent_instance"
            agent_markdown = AGENT_TEMPLATE.format(
                description=instance["description"],
                code_path=json.dumps(base_agent.code_path, indent=2),
                parameters=json.dumps(instance["parameters"], indent=2),
                tools=json.dumps(instance["tools"], indent=2),
            )
            new_agent_page = self.client.create_page(
                book_id=metadata["metadata_book"]["id"],
                chapter_id=metadata["involved_agents"]["chapter_id"],
                name=instance["unique_name"],
                markdown=agent_markdown,
            )
            base_agent.page_id = new_agent_page["id"]
            AgentOnboarding().onboard_agent(base_agent)

        queue = Queue("agents-queue", Redis("redis", 6379))
        pages_to_generate = tape[-1].pages
        # create books & chapters
        books_to_generate = set([p.book for p in pages_to_generate])
        books = {}
        for book in sorted(books_to_generate):
            response = self.client.create_book(book)
            shelf = self.client.get_shelf(self.wiki_context.project_id)
            shelf_book_ids = [b["id"] for b in shelf["books"]] + [response["id"]]
            self.client.update_shelf(self.wiki_context.project_id, books=shelf_book_ids)
            chapters = sorted(
                set([page.chapter for page in pages_to_generate if page.book == book])
            )
            books[book] = {"id": response["id"], "chapters": {}}
            for chapter in chapters:
                chapter_number = extract_number(chapter)
                c = self.client.create_chapter(
                    response["id"], name=chapter, priority=chapter_number
                )
                books[book]["chapters"][chapter] = {"id": c["id"]}

        for page in pages_to_generate:
            agent = AgentsRedisCache().get_agent(page.agent)
            client = AgentBookStackClient(agent.name)
            book_id = books[page.book]["id"]
            chapter_id = books[page.book]["chapters"][page.chapter]["id"]
            page_number = extract_number(page.page)
            page_response = client.create_page(
                book_id=book_id,
                chapter_id=chapter_id,
                name=page.page,
                markdown=f"*Generation in progress:*\n*{page.prompt}*",
                priority=page_number,
            )
            wiki_context = WikiContextInfo(
                page_id=page_response["id"],
                chapter_id=chapter_id,
                book_id=book_id,
                project_context=ProjectContextInfo(
                    project_id=metadata["project_id"],
                    metadata_book_id=metadata["metadata_book"]["id"],
                    tapes_chapter_id=metadata["tapes"]["chapter_id"],
                ),
            )
            queue.enqueue(
                f"{agent.code_path}.generate",
                timeout=600,
                kwargs={
                    "agent_context": agent,
                    "wiki_context": wiki_context,
                    "instructions": page.prompt,
                },
            )
        self.client.update_page(page_id=self.page["id"], markdown=STEP_6)
        save_project_requirements_tape(wiki_context=self.wiki_context, tape=tape)
        return STEP_6_COMMENT


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
