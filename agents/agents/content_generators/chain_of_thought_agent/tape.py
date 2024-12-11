from typing import Any

from agents.content_generators.chain_of_thought_agent.steps import (
    ChainOfThoughtAgentTapeStep,
)
from pydantic import Field
from tapeagents.core import Tape, TapeMetadata
from tapeagents.dialog_tape import DialogContext


class ChainOfThoughtAgentTape(Tape[DialogContext, ChainOfThoughtAgentTapeStep]):
    context: DialogContext = DialogContext(tools=[])
