import json
import pprint

from tinytroupe.factory import TinyPersonFactory

from shared.agent_onboarding import AgentOnboarding
from shared.bookstack_client import AgentBookStackClient
from shared.models import RedisAgent


def create_persona(page_id: int, chapter_id: int):
    client = AgentBookStackClient("WikiAgent")
    context = client.get_chapter(chapter_id)["description"]
    page = client.get_page(page_id)
    AgentOnboarding().onboard_agent(
        RedisAgent(
            name=page["name"],
            type="creative_agent",
            page_id=page_id,
        )
    )
    client = AgentBookStackClient(page["name"])
    bio = page["markdown"]
    p = TinyPersonFactory(context_text=context).generate_person(
        agent_particularities=bio
    )
    agent_spec = p.to_json(suppress=["episodic_memory", "semantic_memory"])
    agent_spec["name"] = page["name"]
    agent_spec["_configuration"]["name"] = page["name"]
    parameters = json.dumps({"tiny_dump": agent_spec}, indent=2)
    # html = f"""<p>{bio}</p><h5>Parameters</h5><pre id="bkmrk-%7B-%22json_serializable"><code class="language-json">{json.dumps(parameters, indent=2)}</code></pre><hr />"""
    markdown = f"""#### Description
{bio}

---

##### Code Path
```json
"agents.creative_feedback_agents.tinytroupe.brainstorm.TinyTroupeBrainstorming"
```
---

##### Command
```json
"/brainstorm"
```
---

##### Parameters

```json
{parameters}

```

---
"""
    client = AgentBookStackClient(page["name"])
    client.update_page(
        page_id,
        markdown=markdown,
        tags=[{"name": "Agent", "value": page["name"]}, {"name": "TinyTroupe"}],
    )

    hello = p.listen_and_act(
        "You have just joined the AI platform WikiAgents! You will assist users in generating creative ideas. Say hello to everyone and briefly summarize your personality! You can use <strong> </strong> tags to highlight words!",
        return_actions=True,
    )
    talks = [t["action"]["content"] for t in hello if t["action"]["type"] == "TALK"]
    if len(talks) > 0:
        comment = f"🚀 {talks[0]}"
    else:
        comment = "🚀 TinyTroupe Person generation finished!"
    client.create_comment(text=comment, page_id=page_id)
