#### Description
LLM Agent that analyzes its grounding content and enriches given prompts with relevant information.
Grounding material can be configured via the `ground_truth` parameter by defining page paths relative to the [Knowledge Base](/shelves/knowledge-bases). 

---

##### Code Path
```json
"agents.content_integrity.grounding.todo"
```
---


##### Parameters
```json
{
  "ground_truth": [
    "<book_name>/<page_name>"
  ]
}
```
---
