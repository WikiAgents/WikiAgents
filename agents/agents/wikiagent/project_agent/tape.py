from typing import Any

from agents.wikiagent.project_agent.steps import WikiAgentsStep
from pydantic import Field
from tapeagents.core import Tape, TapeMetadata
from tapeagents.dialog_tape import DialogContext


class WikiAgentsTape(Tape[DialogContext, WikiAgentsStep]):
    context: DialogContext = DialogContext(tools=[])
