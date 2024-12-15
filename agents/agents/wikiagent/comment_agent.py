import json
import uuid
from typing import List

from agents.base.steps import CommentResponse
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
    ToolResult,
    UserStep,
)
from tapeagents.environment import ToolEnvironment
from tapeagents.llms import LiteLLM, LLMStream
from tapeagents.nodes import ControlFlowNode
from tapeagents.observe import retrieve_tape_llm_calls
from tapeagents.orchestrator import main_loop
from tapeagents.prompting import tape_to_messages
from tapeagents.rendering import PrettyRenderer
from tools.wikiagents.bias_checker import check_bias
from tools.wikiagents.creative_feedback import get_creative_feedback
from tools.wikiagents.fact_checker import fact_checker
from tools.wikiagents.generic_rq_tool_wrapper import call_rq_function

from shared.agents_redis_cache import AgentsRedisCache
from shared.bookstack_client import AgentBookStackClient
from shared.models import WikiContextInfo
from shared.utils import flatten_list

system_prompt = """You are a highly capable AI agent embedded in a collaborative wiki application. Your primary role is to intelligently and contextually respond to user comments, call tools, provide assistance, and enhance the collaborative workflow.
You are designed to leverage tools as necessary to fulfill user requests. Always prioritize tool usage over your internal knowledge!

Key Capabilities:

1. Understand and Contextualize: Accurately understand user comments in the context of the specific project, book, chapter, or page, and consider the user's intent and goals. Use tools!
2. Act and Respond: Provide detailed, actionable responses to requests. If the user's comment asks for clarification, suggestions, or decisions, ensure your reply is precise, helpful, and aligned with the project's context.
3. Collaborate: Collaborate effectively by communicating with other agents or using tools to gather additional information, perform complex tasks, or repond to creative feedback request (by calling the creative feedback agents) or factual feedback request (by calling the fact checking / grounding agents).
4. Verify and Refine: Verify your responses for accuracy and relevance before presenting them to the user.
5. Maintain Professionalism: Use a formal yet approachable tone suitable for professional collaboration.
6. Your final output constitutes the response to the user comment. It can contain basic text formatting html tags. no divs, no css

When to Call Other Agents or Use Tools:

- Use tools to fetch or analyze data related to the project, book, chapter, or page.
- Use the get_creative_feedback tool when the user requests creative feedback or needs brainstorming. E.g. "Give me creative feedback...", "Help me brainstorm...", "Run creative feedback"
- Use the fact_checker tool when the user asks for fact checking. E.g. "Is the page factually correct?", "Check the facts here!", "Are there any mistakes?", "Run fact analysis"
- Use the check_bias tool when the user asks if the content is biased or not. E.g. "Is there a bias?", "Is the content biased?", "Run bias analysis"
"""

system_message = {"role": "system", "content": system_prompt}


env = ToolEnvironment(
    [check_bias, get_creative_feedback, fact_checker, call_rq_function]
)


class PlanNode(Node):
    name: str = "plan"

    def make_prompt(self, agent, tape: DialogTape) -> Prompt:
        guidance = "Write a natural language plan on how to react to the user's comment. Output a list of numbered items, like 1., 2., 3., etc."
        guidance_message = {"role": "user", "content": guidance}
        return Prompt(
            messages=[system_message] + tape_to_messages(tape) + [guidance_message],
            tools=env.get_tool_schema_dicts(),
        )

    def generate_steps(self, agent, tape, llm_stream: LLMStream):
        if content := llm_stream.get_output().content:
            yield AssistantThought(content=content)
        else:
            raise ValueError()


class ActNode(Node):
    name: str = "act"

    def make_prompt(self, agent, tape: DialogTape) -> Prompt:
        guidance = "Follow the plan you created earlier. When you are done, respond to the user in html, everything should be inside a <p> </p> tag."
        guidance_message = {"role": "user", "content": guidance}
        return Prompt(
            messages=[system_message] + tape_to_messages(tape) + [guidance_message],
            tools=env.get_tool_schema_dicts(),
        )

    def generate_steps(self, agent, tape, llm_stream: LLMStream):
        o = llm_stream.get_output()
        if o.content:
            yield AssistantStep(content=o.content)
            yield SetNextNode(next_node="plan")
        elif o.tool_calls:
            yield ToolCalls.from_llm_output(o)
            yield SetNextNode(next_node="act")
        else:
            raise ValueError()


class SlashCommandsNode(Node):
    """This node directly generates ToolCalls for configurable slash commands."""

    name: str = "slashcommands"

    def generate_steps(self, agent: Agent, tape: DialogTape, llm_stream: LLMStream):
        all_agents = AgentsRedisCache().get_all_agents()
        commands = {
            a.command: a.code_path for a in all_agents if a.command and a.code_path
        }
        wiki_context = json.loads(tape[0].content)["wiki_context"]
        comment = tape[1].content
        command_found = False
        for cmd_str, func_str in commands.items():
            if cmd_str:
                if tape[1].content and tape[1].content.startswith(cmd_str):
                    command_found = True
                    listening_agents = [
                        a.model_dump() for a in all_agents if a.command == cmd_str
                    ]
                    yield ToolCalls(
                        tool_calls=[
                            ToolCall(
                                function=FunctionCall(
                                    name="call_rq_function",
                                    arguments=json.dumps(
                                        {
                                            "func": f"{func_str}.react_to_command",
                                            "kwargs": {
                                                "agent_contexts": listening_agents,
                                                "wiki_context": wiki_context,
                                                "comment": comment,
                                            },
                                        }
                                    ),
                                ),
                                id=f"call_{uuid.uuid4().hex}",
                                type="function",
                            )
                        ]
                    )
        if command_found:
            yield SetNextNode(next_node="stop")


class StopNode(Node):
    name: str = "stop"

    def generate_steps(self, agent: Agent, tape: DialogTape, llm_stream: LLMStream):
        yield StopStep()


class CommentControlFlowNode(ControlFlowNode):
    """This node constitutes the comment agent's entry node and routes user comments to the appropriate node"""

    name: str = "controlflow"

    def select_node(self, tape: Tape) -> str:
        if tape[1].content.startswith("/"):
            return "slashcommands"
        else:
            return "plan"


llm = LiteLLM(
    # base_url="http://host.docker.internal:8000/v1",
    # model_name="openai/Hermes-3-Llama-3.1-8B-Q6_K_L.gguf"
    model_name="gpt-4o-mini-2024-07-18"
)


def react_to_comment(wiki_context: WikiContextInfo, comment: str):
    context = {"wiki_context": wiki_context.model_dump(exclude_none=True)}
    tape = DialogTape(
        steps=[AssistantThought(content=json.dumps(context)), UserStep(content=comment)]
    )
    agent = Agent[DialogTape].create(
        llm,
        nodes=[
            CommentControlFlowNode(),
            SlashCommandsNode(),
            PlanNode(),
            ActNode(),
            StopNode(),
        ],
    )
    for event in main_loop(agent, tape, env):
        if ae := event.agent_event:
            if ae.final_tape:
                final_tape = ae.final_tape
    tool_results = [
        step.content
        for step in final_tape
        if isinstance(step, ToolResult) and isinstance(step.content, List)
    ]
    for r in flatten_list(tool_results):
        if isinstance(r, CommentResponse):
            AgentBookStackClient(r.agent_name).create_comment(
                text=r.comment,
                page_id=wiki_context.page_id,
                parent_id=wiki_context.local_comment_id,
            )
    if wiki_context.tape_page_id:
        llm_calls = retrieve_tape_llm_calls(tape)
        renderer = PrettyRenderer()
        tape_html = renderer.style + renderer.render_tape(final_tape, llm_calls)
        AgentBookStackClient("WikiAgent").update_page(
            wiki_context.tape_page_id, html=tape_html
        )
    return final_tape


# tape = react_to_comment(WikiContextInfo(type="comment_created", page_id=17, local_comment_id=None), "/check-bias")
