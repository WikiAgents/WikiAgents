import logging

from agents.wikiagent.project_agent.steps import *

# from agents.wikiagent.project_agent.tape import WikiAgentsTape
from redis import Redis
from rq import Queue
from tapeagents.core import Action, Tape
from tapeagents.environment import Environment
from tapeagents.utils import FatalError

from shared.agents_redis_cache import AgentsRedisCache
from shared.tools_redis_cache import ToolsRedisCache
from shared.bookstack_client import AgentBookStackClient
from shared.models import AgentType
from agents.base.environment import WikiAgentsEnvironment
from agents.base.steps import ActionExecutionFailure

logger = logging.getLogger(__name__)


class ProjectPlannerEnvironment(WikiAgentsEnvironment):
    def react(self, tape: Tape) -> Tape:
        actions = [
            step
            for step in tape.steps[-tape.metadata.n_added_steps :]
            if isinstance(step, Action)
        ]
        tape = super().react(tape)
        for action in actions:
            try:
                match action:
                    case GetAvailableAgentsAction():
                        agents = AgentsRedisCache().get_agents_by_type("content_agent")
                        agents = [
                            {
                                "name": a.name,
                                "page_id": a.page_id,
                                "description": a.description,
                                "parameters": a.parameters,
                                "tools": a.tools,
                            }
                            for a in agents
                        ]
                        tape = tape.append(AvailableAgentsObservation(agents=agents))
                    case GetTools():
                        tools = ToolsRedisCache().get_all_tools()
                        tools = [
                            {"name": t.name, "description": t.description}
                            for t in tools
                        ]
                        tape = tape.append(AllToolsObservation(tools=tools))

            except FatalError:
                raise
            except Exception as e:
                logger.exception(f"Error during action execution: {e}")
                tape = tape.append(ActionExecutionFailure(error=str(e)))
                break
        return tape
