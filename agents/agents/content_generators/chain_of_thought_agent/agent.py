from tapeagents.agent import Agent
from tapeagents.dialog_tape import (
    AssistantStep,
    UserStep,
)
from tapeagents.llms import LiteLLM, LLMStream
from tapeagents.orchestrator import main_loop
from tapeagents.prompting import tape_to_messages


from typing import Any, List
from pydantic import Field
from agents.base.agent import WikiAgentBase
from shared.agents_redis_cache import RedisAgent
from shared.models import WikiContextInfo
from agents.base.nodes import WikiAgentsMonoNode
from agents.base.tape import WikiAgentsTape
from agents.content_generators.chain_of_thought_agent.prompts import PromptRegistry
from agents.content_generators.chain_of_thought_agent.steps import (
    plan_steps,
    act_steps,
    ChainOfThoughtAgentStep,
)
from agents.content_generators.chain_of_thought_agent.tape import (
    ChainOfThoughtAgentTape,
)

from agents.base.environment import WikiAgentsEnvironment
from shared.constants import DEFAULT_LLM
from shared.utils import get_llm
from shared.tools_redis_cache import ToolsRedisCache
from shared.bookstack_client import AgentBookStackClient
from agents.base.utils import get_content_generation_tape, save_content_generation_tape


class PlanActNode(WikiAgentsMonoNode[WikiAgentsTape]):
    system_prompt: str = PromptRegistry.plan_system_prompt
    steps_prompt: str = PromptRegistry.allowed_steps
    allowed_steps: str
    agent_step_cls: Any = Field(exclude=True, default=ChainOfThoughtAgentStep)


class ChainOfThoughtAgent(WikiAgentBase):
    @staticmethod
    def generate(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        instructions: str,
    ) -> str:
        if isinstance(agent_context, dict):
            agent_context = RedisAgent(**agent_context)
        if isinstance(wiki_context, dict):
            wiki_context = WikiContextInfo(**wiki_context)
        tools = []
        if agent_context.tools:
            for tool_name in agent_context.tools:
                tool = ToolsRedisCache().get_tool(tool_name)
                if tool:
                    tools.append(
                        {
                            "tool_name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        }
                    )
        else:
            tools = "You have no access to userdefined tools!"
        llm = get_llm(agent_context)
        env = WikiAgentsEnvironment("WikiAgent")
        tape = get_content_generation_tape(wiki_context, ChainOfThoughtAgentTape)
        if tape is None:
            tape = ChainOfThoughtAgentTape()
        tape = tape.append(UserStep(content=instructions))
        agent = Agent.create(
            llm,
            nodes=[
                PlanActNode(
                    name="plan",
                    system_prompt=agent_context.parameters.get("system_prompt", "")
                    + PromptRegistry.plan_system_prompt.format(userdefined_tools=tools),
                    guidance=PromptRegistry.plan_guidance,
                    allowed_steps=plan_steps,
                    next_node="act",
                ),
                PlanActNode(
                    name="act",
                    system_prompt=agent_context.parameters.get("system_prompt", "")
                    + PromptRegistry.plan_system_prompt.format(userdefined_tools=tools),
                    guidance=PromptRegistry.act_guidance,
                    allowed_steps=act_steps,
                    next_node="plan",
                ),
            ],
        )
        output = None
        for event in main_loop(agent, tape, env, max_loops=10):
            if ae := event.agent_event:
                if isinstance(ae.step, AssistantStep):
                    tape = ae.partial_tape
                    output = ae.step.content
                    break
        assert output is not None
        client = AgentBookStackClient(agent_context.name)
        client.update_page(page_id=wiki_context.page_id, markdown=output)
        save_content_generation_tape(wiki_context, tape)
        return output
