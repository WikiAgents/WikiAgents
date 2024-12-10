from tapeagents.agent import Agent, Node
from tapeagents.core import Prompt, SetNextNode
from tapeagents.dialog_tape import (
    AssistantStep,
    AssistantThought,
    DialogTape,
    ToolCalls,
    UserStep,
)
from tapeagents.environment import ToolEnvironment
from tapeagents.llms import LiteLLM, LLMStream
from tapeagents.orchestrator import main_loop
from tapeagents.prompting import tape_to_messages

today = "2024-09-17"

system_instruction = f"""
You will help the user to learn about financials of companies.
Use as many relevant tools as possible to include more details and facts in your responses.
Today is {today}.
"""
system_message = {"role": "system", "content": system_instruction}

env = ToolEnvironment([])


class PlanNode(Node):
    name: str = "plan"

    def make_prompt(self, agent, tape: DialogTape) -> Prompt:
        guidance = "Write a natural language plan on how to use tools help the user. Output a list of numbered items, like 1., 2., 3., etc."
        guidance_message = {"role": "user", "content": guidance}
        return Prompt(
            messages=[system_message] + tape_to_messages(tape) + [guidance_message],
            tools=env.get_tool_schema_dicts(),
        )

    def generate_steps(self, agent, tape, llm_stream: LLMStream):
        if content := llm_stream.get_output().content:
            yield AssistantThought(content=content)
        else:
            raise ValueError()


class ActNode(Node):
    name: str = "act"

    def make_prompt(self, agent, tape: DialogTape) -> Prompt:
        guidance = "Follow the plan you created to earlier. When you are done, respond to the user."
        guidance_message = {"role": "user", "content": guidance}
        return Prompt(
            messages=[system_message] + tape_to_messages(tape) + [guidance_message],
            tools=env.get_tool_schema_dicts(),
        )

    def generate_steps(self, agent, tape, llm_stream: LLMStream):
        o = llm_stream.get_output()
        if o.content:
            yield AssistantStep(content=o.content)
            yield SetNextNode(next_node="plan")
        elif o.tool_calls:
            yield ToolCalls.from_llm_output(o)
            yield SetNextNode(next_node="act")
        else:
            raise ValueError()
