import os

DEFAULT_LLM = os.environ.get("DEFAULT_LLM", "gpt-4o-mini-2024-07-18")


PROJECT_METADATA_BOOK_NAME = "🗃️ Metadata"
PROJECT_METADATA_BOOK_DESCRIPTION = "Central control for the project."

PROJECT_REQUIREMENTS_TAPE_PAGE_NAME = "📋 Project Requirements Tape"
PAGE_CONTENT_GENERATION_TAPE_PAGE_NAME = "📄 Page ID {page_id} Tape"

PROJECT_REQUIREMENTS_PAGE_NAME = "📋 Project Requirements"

PROJECT_REQUIREMENTS_STEP_1 = """### Step 1/5
---

#### Project Description
{project_description}

---

#### Project Type
Topic Compendium

---

#### Creative Feedback Agents
{configured_creatives}

Available Creative Feedback Agents:
{available_creatives}

---

#### Grounding
{grounding}

---


*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.*    
*Next step: Brainstorming & Project Description Refinement*      
"""


PROJECT_AGENTS_CHAPTER_NAME = "✨ Involved Agents"
PROJECT_AGENTS_CHAPTER_DESCRIPTION = (
    "The agents that are involved in generating this project"
)


PROJECT_CREATIVE_FEEDBACK_CHAPTER_NAME = "🤹‍♀️💡 Creative Feedback Groups"
PROJECT_CREATIVE_FEEDBACK_CHAPTER_DESCRIPTION = "Creative Feedback Groups can brainstorm about your content and give you feedback from targeted perspectives. Comment /feedback on a specific page or on the requirements page to get feedback on the whole project"

PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_NAME = "✅🧠 Content Integrity Agents"
PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_DESCRIPTION = "Content Integrity Agents can review your content for factual mistakes or to ensure grounding with definable sources. Comment /integrity"

PROJECT_TAPES_CHAPTER_NAME = "📼 Tapes"
PROJECT_TAPES_CHAPTER_DESCRIPTION = "The tapes associated with this project"


TOOL_CREATE_COMMENT = "🚀 The tool has been successfully created!"
TOOL_UPDATE_COMMENT = "🚀 The tool has been successfully updated!"
TOOL_FAILED_COMMENT = "💥 Natural language tool generation not supported yet! Tool pages must contain python code in triple quotes."
