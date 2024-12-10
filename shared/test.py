md = """##### Description
An agent that uses Chain of Thought to accomplish tasks.

---

##### Code Path
```json
agents.content_generators.chain_of_thought_agent.agent.ChainOfThoughAgent
```
---

##### Command
```json
```
---

##### Parameters
```json
{
  "system_prompt": "foobar",
  "temperature": 0.3
}
```
---
##### Tools


---
"""


def sanitize_json_completion(completion: str) -> str:
    """
    Return only content inside the first pair of triple backticks if they are present.
    """
    tiks_counter = 0
    lines = completion.strip().split("\n")
    clean_lines = []
    for line in lines:
        if line.startswith("```"):
            tiks_counter += 1
            if tiks_counter == 1:
                clean_lines = []
            elif tiks_counter == 2:
                break
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines)


from shared.utils import extract_section_content

params = extract_section_content(md, "##### Parameters")

j = sanitize_json_completion(params)
