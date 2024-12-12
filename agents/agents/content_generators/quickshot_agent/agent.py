from tapeagents.agent import Agent
from tapeagents.dialog_tape import (
    AssistantStep,
    UserStep,
)
from tapeagents.llms import LiteLLM
from tapeagents.orchestrator import main_loop


from typing import Any, List
from pydantic import Field
from agents.base.agent import WikiAgentBase
from shared.agents_redis_cache import RedisAgent
from shared.models import WikiContextInfo
from agents.base.nodes import WikiAgentsMonoNode
from agents.base.tape import WikiAgentsTape
from agents.base.tape import WikiAgentsTape
from agents.base.environment import WikiAgentsEnvironment
from agents.base.steps import WikiAgentsStep
from tapeagents.utils import get_step_schemas_from_union_type
from typing import Annotated, List, Literal, Optional, TypeAlias, Union
from tapeagents.dialog_tape import AssistantStep, UserStep
from shared.constants import DEFAULT_LLM
from shared.utils import get_llm


ALLOWED_STEPS = """
You are allowed to produce ONLY steps with the following json schemas:
{allowed_steps}
Do not reproduce schema when producing the steps, use it as a reference.
"""

allowed_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[UserStep, AssistantStep],
        Field(discriminator="kind"),
    ]
)


class QuickShotNode(WikiAgentsMonoNode[WikiAgentsTape]):
    system_prompt: str = ""
    steps_prompt: str = ALLOWED_STEPS
    allowed_steps: str
    agent_step_cls: Any = Field(exclude=True, default=WikiAgentsStep)


class QuickShotAgent(WikiAgentBase):
    @staticmethod
    def generate(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        instructions: str,
    ) -> str:
        llm = get_llm(agent_context)
        env = WikiAgentsEnvironment("Quick Shot Agent")
        tape = WikiAgentsTape(
            steps=[
                UserStep(
                    content=instructions,
                )
            ]
        )
        agent = Agent.create(
            llm,
            nodes=[
                QuickShotNode(
                    name="quickshot",
                    system_prompt=agent_context.parameters.get("sytem_prompt", ""),
                    guidance="Respond to the users' request",
                    allowed_steps=allowed_steps,
                    next_node="quickshot",
                ),
            ],
        )
        for event in main_loop(agent, tape, env, max_loops=1):
            if ae := event.agent_event:
                if isinstance(ae.step, AssistantStep):
                    tape = ae.partial_tape
                    break
        return tape
