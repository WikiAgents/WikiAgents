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
   - Represent abstract key concepts as Chapters.
   - Divide subtopics or deliverables into Pages within each Chapter.
   - Chapters should contain several pages. If is has too few pages, make the chapter more abstract.
   
2. Detailed Structure: 
   - Use up to three Books, each representing an abstract high level concept.
   - Organize related concepts and subtopics as Chapters within each Book.
   - Use Pages for specific deliverables, explanations, or fine-grained content within each Chapter.
   - Chapters should contain several pages. If is has too few pages, make the chapter more abstract.

ALWAYS use descriptive page names! DO NOT name them Page 1, Page 2, ...
The output structure must cover ONLY key_components from the final_requirements_refinement! Use the key components as outer containers (e.g. as book or as chapter) and structure the details of the component into pages.
DO NOT INCLUDE COMPONENTS OTHER THAN THOSE IN final_requirements_refinement! Ignore the key components of previous refinements!

Respond with kind="project_output_structure_suggestion"

Here is an example of the expected structure schema for the simple_structure and detailed_structure:
{
   "1. book1_name":
   {
      "1. chapter1_name": {
         "1. page1_name": "short description of what the page contains",
         "2. page2_name": "short description of what the page contains",
         "3. page3_name": "short description of what the page contains",
         "4. page4_name": "short description of what the page contains",
         "5. page5_name": "short description of what the page contains",
      },
      "2. chapter2_name": {
         "1. page1_name": "short description of what the page contains",
         "2. page2_name": "short description of what the page contains",
         "3. page3_name": "short description of what the page contains",
         "4. page4_name": "short description of what the page contains",
         "5. page5_name": "short description of what the page contains",
      },
      ...      
   }
}

Make sure to always add numberings to the books, chapters and pages to preserve the order!

"""
    + short_format_instruction
)


SELECT_AGENTS = (
    f"""
Your task is to select agents from the available agents in the system, suited for generating the project. Follow these steps:

1. Retrieve Available Agents: Use the tool get_available_agents to list all available agents and their capabilities. Respond with kind="get_available_agents"

2. Analyze Project Needs: Review the refined_description and key_components in the final_requirements_refinement to identify the roles and skills required for successful content generation.

3. Select Agents: Match the available agents to the required roles based on their capabilities. Output the agent names, corresponding page_ids, and give a reason why the agent was selected. Respond with kind="agent_selection_thought"

4. Retrieve Tools: Use the tool get_all_tools to list all available tools. You can assign tools to agents in the next step. Respond with kind="get_all_tools"

5. Define Agent Instances: Create instances of your selected agents (e.g. one instance for each required expert w.r.t. key components, max. 8 agent instances, min. 3). Each selected agent can be instantiated multiple times with adjusted configurations. For each agent instance, provide a unique_name, the page_id of the original agent, description, parameters and tools. Only adjust parameters that are already defined in the original agent (if the original exposes a parameter, it means that you are encouraged to adjust the value of the parameter)! If a parameter name contains 'system_prompt' or 'additional_system_prompt' it means you can adjust the persona of the agent, be specific and create highly skilled, top notch system prompts (e.g. 'You are a high-skilled expert in the domain of ...'). The description must be in alignment with the configured parameters (e.g. adjusted prompt) and tools! You are allowed to modify the tools list of each agent instance. Provide valid tool names. Respond with kind="agent_instances_thought"

"""
    + short_format_instruction
)

PAGE_INSTRUCTIONS = (
    """Your task is to assign an agent to each page and to generate a detailed prompt that will be used to generate the page content.

Choose from these agents: 
{agents}

Here are the pages, add the agent and prompt to each:
{pages}

Understand the page descriptions and generate the prompt that is used to generate the page content.
Ensure every page has an agent assigned and a detailed prompt

When you are done, respond with kind='page_instructions_thought'

"""
    + short_format_instruction
)


# PAGE_INSTRUCTIONS = """Your task is to assign an agent from agent_instances (in agent_instances_thought) to each page in the selected project_output_structure_suggestion. The final output will be of kind='page_instructions_thought'
# Follow these steps:

# 1. Review agent_instances in agent_instances_thought to understand their roles and capabilities. Respond with kind='agent_instance_names'
# 2. Analyze the chosen project_output_structure_suggestion to identify all pages. Respond with kind='pages_thought'
# 3. Match the most suitable agent instance to each page based on its function and requirements.
# 4. Define detailed prompts for generating each page. Make sure to include the context of the page (book, chapter).
# 5. Ensure every page is assigned an agent instance and a prompt, with no omissions.

# When you are done, respond with kind='page_instructions_thought'

# """ + short_format_instruction


class PromptRegistry:
    system_prompt = SYSTEM_PROMPT
    allowed_steps = ALLOWED_STEPS
    project_requirements_refinement = REQUIREMENTS_REFINEMENT
    brainstorming_incorporation = BRAINSTORMING_RESULTS_INCORPORATION
    final_requirements_refinement = FINAL_REQUIREMENTS_REFINEMENT
    output_structure_suggestion = OUTPUT_STRUCTURE_SUGGESTION
    select_agents = SELECT_AGENTS
    page_instructions = PAGE_INSTRUCTIONS
