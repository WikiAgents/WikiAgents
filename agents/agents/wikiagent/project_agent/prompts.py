# 1. **Refining Initial Requirements:**
#    - Analyze the user's input for clarity, completeness, and detail.
#    - Generate improved and comprehensive project requirements from the user's description.
#    - Ensure that the refined requirements aligns with the user's goals.


# 2. **Propose an Output Structure:**
#    - Design an appropriate hierarchical output structure for the project:
#      - A **Book** serves as top-level containers for the project's main topics or components. Simple project may require only one book, but in general you should always prefer the highest degree of structure and comprehensiveness.
#      - **Chapters** organize content into logical subtopics or areas of focus.
#      - **Pages** represent the most detailed level, containing specific deliverables or explanations. Pages contain the actual content.
#    - The structure must include at least one Book and one Page but should aim for maximum detail and coherence based on the project scope. In general, you should always prefer the highest degree of structure and comprehensiveness.


# 3. **Select Suitable Agents:**
#    - Retrieve a list of all available agents in the system.
#    - Identify the agents best suited to the project's needs.
#    - Include a brief explanation for why each selected agent is relevant.


SYSTEM_PROMPT = """You are a high-skilled AI Project Planner and Structuring Agent, specializing in organizing and refining AI-generated projects of various kinds.
Your primary goal is to ensure that projects are clear, structured, and executed with optimal efficiency.
Keep your replies concise and direct. Prioritize clarity and avoid over-elaboration.
Do not express your emotions or opinions about the user questions.
"""


short_format_instruction = "DO NOT OUTPUT ANYTHING BESIDES THE JSON. It will break the system that processes the output."


ALLOWED_STEPS = """
You are allowed to produce ONLY steps with the following json schemas:
{allowed_steps}
Do not reproduce schema when producing the steps, use it as a reference.
"""

REQUIREMENTS_REFINEMENT = f"""
1. **Understand the Input:**
   - Carefully read and analyze the `initial_project_description` provided in the `project_metadata`. Identify the core topic, objectives, and any key details, paying special attention to the scope and specific goals of the project.

2. **Expand Scope:**
   - Break down the project into its main components and subtopics. Ensure that you address all critical aspects that are implied or explicitly mentioned in the description.

3. **Refine and Reorganize:**
   - Rephrase the project description for clarity, coherence, and completeness. Structure the description logically, ensuring that it reflects the key objectives, expected deliverables, and any sub-tasks or milestones necessary for successful execution.
   - Ensure that the restructured description is in alignment with the user's original intent and purpose of the project.

4. **Summarize Clearly:**
   - Provide a polished, detailed, and comprehensive version of the project description that can serve as a clear guide for the planning and execution phases. This final description should be well-organized, actionable, and ensure all key components of the project are well-defined and addressed.

Respond with kind="project_requirements_refinement".
{short_format_instruction}
"""

BRAINSTORMING_RESULTS_INCORPORATION = (
    """Review the brainstorming summary provided below. Integrate any relevant ideas, suggestions, or insights from this summary into the project description. Ensure that the refined description reflects the expanded scope and addresses any new perspectives or improvements suggested during brainstorming.
Brainstorming summary:
{brainstorming_summary}

Respond with kind="project_requirements_refinement".

"""
    + short_format_instruction
)

FINAL_REQUIREMENTS_REFINEMENT = (
    """Review all previous project_requirements_refinement documents and ensure that every key element, goal, and requirement has been addressed clearly and completely. Synthesize any updates, changes, or additions made throughout the refinement process. Based on this, create a polished and comprehensive final_requirements_refinement that consolidates all relevant details, providing a clear, actionable, and well-structured summary of the project’s requirements written in present tense. Ensure the final version is fully aligned with the user’s objectives and ready for implementation."""
    + short_format_instruction
)


OUTPUT_STRUCTURE_SUGGESTION = (
    """Your task is to suggest both a simple and a detailed hierarchical structure to organize the key components from the final_requirements_refinement in your previous step effectively. Adhere to these principles:

- Books: Represent top-level containers for main topics or components.
- Chapters: Organize content into logical subtopics or areas of focus within a book.
- Pages: Provide the most detailed level, containing specific deliverables, explanations, or content.

Guidelines:
1. Simple Structure: 
   - Use one Book for the entire project. Use the project name as book name.
   - Represent key components as Chapters.
   - Divide subtopics or deliverables into Pages within each Chapter.
   
2. Detailed Structure: 
   - Use multiple Books, each representing a key component.
   - Organize related subtopics as Chapters within each Book.
   - Use Pages for specific deliverables, explanations, or fine-grained content within each Chapter.

Your suggestions should ensure logical flow, coherence, and comprehensiveness while reflecting the projects' key components.

Respond with kind="project_output_structure_suggestion"

Here is an example of the expected structure schema for the simple_structure and detailed_structure:
{
   "book1_name":
   {
      "chapter1_name": {
         "page1_name": "short page description",
         "page2_name": "short page description"
      },
      "chapter2_name": {
         "page1_name": "short page description"
      },      
   }
}

"""
    + short_format_instruction
)


SELECT_AGENTS = f"""
Your task is to select agents from the available agents in the system, suited for generating the project. You should suggest adjusted parameters for the selected agents aswell. Only suggest adjustments for parameter that are already defined in the agent! Follow these steps:

1. Retrieve Available Agents: Use the tool get_available_agents to list all available agents and their capabilities. Respond with kind="get_available_agents"

2. Analyze Project Needs: Review the refined_description and key_components in the final_requirements_refinement to identify the roles and skills required for successful content generation.

3. Select Agents: Match the available agents to the required roles based on their capabilities. Choose the most fitting agents for each role and recommend adjusted parameters for this agent. Only suggest parameter changes for parameters that are already defined! You can instanciate the same agent (same name and page_id) with adjusted parameters multiple times! Respond with kind="agent_selection_thought"

"""
# Respond with kind="agent_selection_thought"
# {short_format_instruction}


class PromptRegistry:
    system_prompt = SYSTEM_PROMPT
    allowed_steps = ALLOWED_STEPS
    project_requirements_refinement = REQUIREMENTS_REFINEMENT
    brainstorming_incorporation = BRAINSTORMING_RESULTS_INCORPORATION
    final_requirements_refinement = FINAL_REQUIREMENTS_REFINEMENT
    output_structure_suggestion = OUTPUT_STRUCTURE_SUGGESTION
    select_agents = SELECT_AGENTS
