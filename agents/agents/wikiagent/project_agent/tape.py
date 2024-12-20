from typing import Any

from agents.wikiagent.project_agent.steps import ProjectPlannerAgentTapeStep
from pydantic import Field
from tapeagents.core import Tape, TapeMetadata
from tapeagents.dialog_tape import DialogContext


class ProjectPlannerTape(Tape[DialogContext, ProjectPlannerAgentTapeStep]):
    context: DialogContext = DialogContext(tools=[])
