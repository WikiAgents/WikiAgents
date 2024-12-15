STEP_2 = """### Step 2/4
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

STEP_3 = """### Step 3/4
#### Output Structure

##### Simple
{simple_structure}

---

##### Detailed
{detailed_structure}

---

*Edit the output structure to your liking and  write `/next simple` or `/next detailed` in the comments to proceed.*
"""

STEP_4 = """### Step 4/4
#### Selected Agents
{selected_agents}

---

#### Agent Instances
{agent_instances}

---


*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.* 
"""

STEP_1_COMMENT = "🚀"
STEP_2_COMMENT = "🚀 The Project Description Refinement step has been completed. Please review the refinement and feel free to edit the page to your liking. To proceed to the next step, comment <strong>/next</strong>."
STEP_3_COMMENT = "🚀 You have completed the Output Structure Suggestion step. Please review and edit the structure to fit your needs, and choose between a simple or a detailed structure. You can proceed to the next step by commenting <strong>/next simple</strong> for a simple structure or <strong>/next detailed</strong> for a detailed structure."
STEP_4_COMMENT = "🚀 I have selected some agents for the project, please review and edit to your liking. Type <strong>/next</strong> to start to generation!"
