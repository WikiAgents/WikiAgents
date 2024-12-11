from typing import Any

from agents.base.steps import WikiAgentsTapeStep
from pydantic import Field
from tapeagents.core import Tape, TapeMetadata
from tapeagents.dialog_tape import DialogContext


class WikiAgentsTape(Tape[DialogContext, WikiAgentsTapeStep]):
    context: DialogContext = DialogContext(tools=[])
