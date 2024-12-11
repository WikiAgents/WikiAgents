import logging

from agents.wikiagent.project_agent.steps import *

# from agents.wikiagent.project_agent.tape import WikiAgentsTape
from redis import Redis
from rq import Queue
from tapeagents.core import Action, Tape
from tapeagents.environment import Environment
from tapeagents.utils import FatalError

from shared.agents_redis_cache import AgentsRedisCache
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
                        agents = [
                            a.model_dump(exclude_none=True)
                            for a in AgentsRedisCache().get_all_agents()
                            if a.type == "content_agent"
                        ]
                        tape = tape.append(AvailableAgentsObservation(agents=agents))

            except FatalError:
                raise
            except Exception as e:
                logger.exception(f"Error during action execution: {e}")
                tape = tape.append(ActionExecutionFailure(error=str(e)))
                break
        return tape
