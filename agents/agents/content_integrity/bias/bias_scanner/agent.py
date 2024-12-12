import json
from typing import List, Literal, Optional

from agents.base.agent import WikiAgentBase
from agents.content_integrity.bias.bias_scanner.prompts import PromptRegistry
from agents.content_integrity.bias.bias_scanner.result_rendering import render_result
from agents.base.steps import CommentResponse
from tapeagents.agent import Agent, Node
from tapeagents.core import Action, Prompt, SetNextNode, Tape, Thought
from tapeagents.dialog_tape import (
    AssistantStep,
    AssistantThought,
    DialogContext,
    DialogStep,
    DialogTape,
    UserStep,
)
from tapeagents.llms import LiteLLM, LLMStream
from tapeagents.prompting import tape_to_messages, view_to_messages
from tapeagents.team import TeamAgent, TeamTape
from tapeagents.utils import sanitize_json_completion

from shared.bookstack_client import AgentBookStackClient
from shared.constants import (
    PROJECT_CREATIVE_FEEDBACK_CHAPTER_NAME,
    PROJECT_METADATA_BOOK_NAME,
)
from shared.models import RedisAgent, WikiContextInfo
from shared.utils import get_llm


class BiasScannerResult(Action):
    kind: Literal["biasscanner_result"] = "biasscanner_result"
    result: dict


BiasScannerTape = Tape[str, BiasScannerResult | DialogContext | DialogStep]


class LanguageDetectorNode(Node):
    name: str = "language_detector"

    def make_prompt(self, agent, tape: BiasScannerTape) -> Prompt:
        view = agent.compute_view(tape)
        guidance = "Is the input text written in English or German? Your response should contain English or German, nothing else!"
        guidance_message = {"role": "user", "content": guidance}
        return Prompt(messages=view_to_messages(view.top, agent) + [guidance_message])

    def generate_steps(self, agent, dialog, llm_stream: LLMStream):
        if content := llm_stream.get_output().content:
            language = "english"
            if "german" in content.lower():
                language = "german"
            yield SetNextNode(next_node="biasscanner")
            yield AssistantThought(content=language)
        else:
            raise ValueError()


class BiasScannerNode(Node):
    name: str = "biasscanner"

    def make_prompt(self, agent, tape: BiasScannerTape) -> Prompt:
        language = tape[-1].content
        system_prompt = (
            PromptRegistry.system_prompt_de
            if language == "german"
            else PromptRegistry.system_prompt_en
        )
        return Prompt(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": tape[0].content},
            ]
        )

    def generate_steps(self, agent, dialog, llm_stream: LLMStream):
        if content := llm_stream.get_output().content:
            result = json.loads(sanitize_json_completion(content))
            yield SetNextNode(next_node="language_detector")
            yield BiasScannerResult(result=result)
        else:
            raise ValueError()


class BiasScanner(WikiAgentBase):
    @staticmethod
    def react_to_comment(
        agent_context: RedisAgent | dict,
        wiki_context: WikiContextInfo | dict,
        comment: str,
    ) -> List[CommentResponse]:
        if isinstance(agent_context, dict):
            agent_context = RedisAgent(**agent_context)
        if isinstance(wiki_context, dict):
            wiki_context = WikiContextInfo(**wiki_context)
        llm = get_llm(agent_context)
        client = AgentBookStackClient("BiasScanner")
        page_markdown = client.export_page(wiki_context.page_id, export_type="markdown")
        agent = Agent.create(
            name="BiasScanner",
            nodes=[LanguageDetectorNode(), BiasScannerNode()],
            llms=llm,
        )
        input_tape = BiasScannerTape(steps=[UserStep(content=page_markdown)])
        final_tape = agent.run(input_tape).get_final_tape()
        assert isinstance(final_tape[-1], BiasScannerResult)
        html = render_result(final_tape[-1].result)
        return [CommentResponse(agent_name="BiasScanner", comment=html)]

    @staticmethod
    def react_to_command(
        agent_contexts: List[RedisAgent], wiki_context: WikiContextInfo, comment: str
    ) -> List[CommentResponse]:
        if isinstance(agent_contexts[0], dict):
            agent_contexts = [
                RedisAgent(**agent_context) for agent_context in agent_contexts
            ]
        if isinstance(wiki_context, dict):
            wiki_context = WikiContextInfo(**wiki_context)
        llm = get_llm(agent_contexts[0])
        client = AgentBookStackClient("BiasScanner")
        page_markdown = client.export_page(wiki_context.page_id, export_type="markdown")
        agent = Agent.create(
            name="BiasScanner",
            nodes=[LanguageDetectorNode(), BiasScannerNode()],
            llms=llm,
        )
        input_tape = BiasScannerTape(steps=[UserStep(content=page_markdown)])
        final_tape = agent.run(input_tape).get_final_tape()
        assert isinstance(final_tape[-1], BiasScannerResult)
        html = render_result(final_tape[-1].result)
        return [CommentResponse(agent_name="BiasScanner", comment=html)]
