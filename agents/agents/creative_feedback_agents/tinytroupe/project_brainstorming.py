from typing import List, Optional

from shared.models import RedisAgent, WikiContextInfo
from agents.creative_feedback_agents.tinytroupe.wikiworld import TinyWikiWorld
from tinytroupe.agent import TinyPerson
from agents.base.steps import CommentResponse


# PRB_PROMPT = """You are invited to contribute your thoughts and ideas to the following topic:
# {project_description}


# As you reflect on this subject:

# 1. Identify key components or elements that define the topic.
# 2. Consider questions or aspects that might arise when analyzing or discussing the topic.
# 3. Share examples or ideas that help illustrate these components.
# 4. Respectfully build on or critique others’ contributions to enhance the collective understanding.

# Take your time to think deeply and collaborate creatively. Let’s uncover all the essential aspects of this topic together!
# """

PRB_PROMPT = """You're part of a collaborative wiki-like system where we create textual projects together. Take a moment to think carefully about this project. 

Project Type:
{project_type}

Project Description:
{project_description}


Focus on:

1. What the project is about.
2. Its key components or areas to explore.
3. Any gaps or questions that might need addressing.

Once you've thought it through, start talking! Share your ideas, ask questions, and build on what others say. Let's turn these thoughts into a lively, productive discussion! When you respond to someone, always include a new aspect!
"""


SUMMARY_PROMPT = """Can you please consolidate the ideas that the group came up with? Provide a lot of details on each idea, and complement anything missing.
Format the key points as html list in your output like so: <ul><li>Example</li><li>Example2</li></ul>. Use the <strong> tag to highlight words! Only output the list, nothing else.
"""


def project_requirements_brainstorming(
    agent_contexts: List[RedisAgent] | List[dict],
    wiki_context: WikiContextInfo | dict,
    project_description: str,
    project_type: str,
    rounds: int = 3,
):
    if isinstance(agent_contexts[0], dict):
        agent_contexts = [
            RedisAgent(**agent_context) for agent_context in agent_contexts
        ]
    if isinstance(wiki_context, dict):
        wiki_context = WikiContextInfo(**wiki_context)
    agents = [
        TinyPerson.load_spec(a.parameters["tiny_dump"])
        for a in agent_contexts
        if a.parameters and "tiny_dump" in a.parameters
    ]
    world = TinyWikiWorld("Focus group", agents)
    world.communication_display = False
    world.set_wiki_context(
        page_id=wiki_context.page_id, comment_id=wiki_context.local_comment_id
    )
    world.make_everyone_accessible()
    world.broadcast(
        PRB_PROMPT.format(
            project_type=project_type, project_description=project_description
        )
    )
    world.run(rounds)
    summarizer = world.get_agent_by_name(agents[0].name)
    summary = summarizer.listen_and_act(SUMMARY_PROMPT, return_actions=True)
    talks = [t["action"]["content"] for t in summary if t["action"]["type"] == "TALK"]
    if len(talks) == 0:
        return [
            CommentResponse(
                agent_name=agents[0].name,
                comment="💥 Everyone's so deep in thought, they forgot to come back with answers! Try to refine the goal.",
            )
        ]
    summary_comment = "🚀 Here is a summary of the discussion:\n" + ". ".join(talks)
    return [CommentResponse(agent_name=agents[0].name, comment=summary_comment)]
