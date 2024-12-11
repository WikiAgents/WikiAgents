from tapeagents.nodes import ControlFlowNode, MonoNode
from pydantic import Field
from typing import Any, Generic, TypeVar
from agents.base.steps import WikiAgentsStep
from agents.base.tape import WikiAgentsTape


# StepType = TypeVar("StepType")
TapeType = TypeVar("TapeType")


class WikiAgentsMonoNode(MonoNode, Generic[TapeType]):
    system_prompt: str
    steps_prompt: str
    allowed_steps: str
    agent_step_cls: Any = Field(exclude=True, default=None)

    def get_steps_description(self, tape: TapeType, agent: Any) -> str:
        """
        Allow different subset of steps based on the agent's configuration
        """
        return self.steps_prompt.format(allowed_steps=self.allowed_steps)
