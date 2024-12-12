import os

DEFAULT_LLM = os.environ.get("DEFAULT_LLM", "gpt-4o-mini-2024-07-18")


PROJECT_METADATA_BOOK_NAME = "🗃️ Metadata"
PROJECT_METADATA_BOOK_DESCRIPTION = "Central control for the project."

PROJECT_REQUIREMENTS_TAPE_PAGE_NAME = "📋 Project Requirements Tape"


PROJECT_REQUIREMENTS_PAGE_NAME = "📋 Project Requirements"

PROJECT_REQUIREMENTS_STEP_1 = """### Step 1/4
---

#### Project Description
{project_description}

---

*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.*    
*Next step: Project Description Refinement*      
"""

PROJECT_REQUIREMENTS_STEP_2 = """### Step 2/4
#### Project Description
{project_description}

---

#### Key Components
{key_components}

---

*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.*    
*Next step: Agent Selection*    
"""

PROJECT_REQUIREMENTS_STEP_2_COMMENT = "🚀 The Project Description Refinement step has been completed. Please review the refinement and feel free to edit the page to your liking. To proceed to the next step, comment <strong>/next</strong>."

PROJECT_REQUIREMENTS_STEP_3 = """### Step 3/4
#### Output Structure

##### Simple
{simple_structure}

---

##### Detailed
{detailed_structure}

---


*Edit the output structure to your liking and  write `/next simple` or `/next detailed` in the comments to proceed.*
"""

PROJECT_REQUIREMENTS_STEP_3_COMMENT = "🚀 You have completed the Output Structure Suggestion step. Please review and edit the structure to fit your needs, and choose between a simple or a detailed structure. You can proceed to the next step by commenting <strong>/next simple</strong> for a simple structure or <strong>/next detailed</strong> for a detailed structure."

PROJECT_REQUIREMENTS_STEP_4 = """### Step 4/4
#### Chosen Agents
{selected_agents}

---

#### Agent Hiring Suggestions
{missing_roles}

---

*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.*    
"""

PROJECT_REQUIREMENTS_STEP_4_COMMENT = "🚀 I have selected some agents for the project, please review and edit to your liking. Type <strong>/next</strong> to start to generation!"


PROJECT_REQUIREMENTS_PAGE_MARKDOWN = """
### Task Description
{task_description}

---

### Project type
e.g. Knowledge Base, Code, Project Management

---

### Assigned Agents


---
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
