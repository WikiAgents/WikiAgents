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


class PlanActNode(WikiAgentsMonoNode[WikiAgentsTape]):
    system_prompt: str = PromptRegistry.plan_system_prompt
    steps_prompt: str = PromptRegistry.allowed_steps
    allowed_steps: str
    agent_step_cls: Any = Field(exclude=True, default=ChainOfThoughtAgentStep)


userdefined_actions = [{"function": "get_recipies", "parameters": {}}]


class ChainOfThoughAgent(WikiAgentBase):
    @staticmethod
    def generate(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        instructions: str,
    ) -> str:
        llm = get_llm(agent_context)
        env = WikiAgentsEnvironment("WikiAgent")
        tape = ChainOfThoughtAgentTape(
            steps=[
                UserStep(
                    content=instructions,
                )
            ]
        )
        agent = Agent.create(
            llm,
            nodes=[
                PlanActNode(
                    name="plan",
                    system_prompt=PromptRegistry.plan_system_prompt.format(
                        userdefined_actions=userdefined_actions
                    )
                    + agent_context.parameters.get("additional_system_prompt", ""),
                    guidance=PromptRegistry.plan_guidance,
                    allowed_steps=plan_steps,
                    next_node="act",
                ),
                PlanActNode(
                    name="act",
                    system_prompt=PromptRegistry.plan_system_prompt.format(
                        userdefined_actions=userdefined_actions
                    )
                    + agent_context.parameters.get("additional_system_prompt", ""),
                    guidance=PromptRegistry.act_guidance,
                    allowed_steps=act_steps,
                    next_node="plan",
                ),
            ],
        )
        for event in main_loop(agent, tape, env, max_loops=5):
            if ae := event.agent_event:
                if isinstance(ae.step, AssistantStep):
                    tape = ae.partial_tape
                    break
        return tape
