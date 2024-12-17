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
from shared.bookstack_client import AgentBookStackClient
from shared.tools_redis_cache import ToolsRedisCache
from agents.base.utils import get_content_generation_tape, save_content_generation_tape
from agents.base.steps import UserDefinedTool, UserDefinedToolObservation


ALLOWED_STEPS = """
You are allowed to produce ONLY steps with the following json schemas:
{allowed_steps}
Do not reproduce schema when producing the steps, use it as a reference.
"""

SYSTEM_PROMPT = """Use as many relevant tools/actions as possible to include more details and facts in your responses.
You can use the following userdefined_actions:
{userdefined_tools}

DON'T MAKE UP USERDEFINED ACTIONS! ONLY USED USERDEFINED ACTIONS THAT ARE LISTED ABOVE!

"""

allowed_steps = get_step_schemas_from_union_type(
    Annotated[
        Union[AssistantStep, UserDefinedTool, UserDefinedToolObservation],
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
        env = WikiAgentsEnvironment("Quick Shot Agent")
        tape = get_content_generation_tape(wiki_context, WikiAgentsTape)
        if tape is None:
            tape = WikiAgentsTape()
        tape = tape.append(UserStep(content=instructions))
        agent = Agent.create(
            llm,
            nodes=[
                QuickShotNode(
                    name="quickshot",
                    system_prompt=agent_context.parameters.get("system_prompt", "")
                    + SYSTEM_PROMPT.format(userdefined_tools=tools),
                    guidance="Respond to the users' request in well-structured markdown. The largest heading to use is ####. Respond with kind='assistant'",
                    allowed_steps=allowed_steps,
                    next_node="quickshot",
                ),
            ],
        )
        for event in main_loop(agent, tape, env, max_loops=1):
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
        # return tape
