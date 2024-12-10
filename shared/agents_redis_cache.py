import json
from typing import List, Literal

from redis import Redis

from shared.models import RedisAgent


class AgentsRedisCache:
    def __init__(self):
        self.redis = Redis("redis", decode_responses=True)

    def update_agent(self, agent: RedisAgent):
        parameters = {}
        if agent.parameters:
            parameters = agent.parameters.copy()
        tools = {}
        if agent.tools:
            tools = agent.tools.copy()
        agent.parameters = None
        agent.tools = None
        self.redis.hset(
            f"agent:{agent.name}", mapping=agent.model_dump(exclude_none=True)
        )
        if parameters:
            self.redis.hset(
                f"agent:{agent.name}:parameters",
                mapping={k: json.dumps(v) for k, v in parameters.items()},
            )
        if tools:
            self.redis.hset(
                f"agent:{agent.name}:tools",
                mapping={k: json.dumps(v) for k, v in tools.items()},
            )

    def get_agent(self, name: str):
        agent = RedisAgent(**self.redis.hgetall(f"agent:{name}"))
        agent.parameters = self.redis.hgetall(f"agent:{name}:parameters")
        agent.tools = {
            k: json.loads(v)
            for k, v in self.redis.hgetall(f"agent:{name}:tools").items()
        }
        return agent

    def delete_agent(self, name: str):
        self.redis.delete(f"agent:{name}")
        self.redis.delete(f"agent:{name}:parameters")
        self.redis.delete(f"agent:{name}:tools")

    def get_all_agents(self):
        keys = []
        cursor = 0
        while True:
            cursor, batch = self.redis.scan(cursor=cursor, match="agent:*")
            keys.extend(batch)
            if cursor == 0:
                break
        pipeline = self.redis.pipeline()
        for agent_key in keys:
            if agent_key.endswith(":parameters") or agent_key.endswith(":tools"):
                continue
            pipeline.hgetall(agent_key)
        agents = pipeline.execute()
        agents = [RedisAgent(**a) for a in agents]
        for a in agents:
            a.parameters = {
                k: json.loads(v)
                for k, v in self.redis.hgetall(f"agent:{a.name}:parameters").items()
            }
            a.tools = {
                k: json.loads(v)
                for k, v in self.redis.hgetall(f"agent:{a.name}:tools").items()
            }
        return agents

    def get_agents_by_type(
        self,
        type: Literal[
            "content_agent", "creative_agent", "integrity_agent", "wikiagent"
        ],
    ):
        return [a for a in self.get_all_agents() if a.type == type]


# ag = RedisAgent(name="test", type="content_agent", tools={"tool1": {"page_id": 1, "description": "foo"}}, parameters={"temp": 1.1})