STEP_2 = """### Step 2/5
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

STEP_3 = """### Step 3/5
#### Output Structure

##### Simple
{simple_structure}

---

##### Detailed
{detailed_structure}

---

*Edit the output structure to your liking and  write `/next simple` or `/next detailed` in the comments to proceed.*
"""

STEP_4 = """### Step 4/5
#### Selected Agents
{selected_agents}

---

#### Agent Instances
{agent_instances}

---


*Write a `/next` comment to proceed.*   
*Edit the page if you want to make changes.* 
"""


STEP_5 = """### Step 5/5
#### Page Generation Instructions & Agent Assignment
{page_instructions}

---



*Write a `/next` comment to start the content generation.*   
*Edit the page if you want to make changes.* 
"""

STEP_6 = """### Wizard End

**Page Generation in Progress!**  
- Pages **queued for generation** are tagged with: **State: Waiting**  
- Pages **currently being generated** are tagged with: **State: Generation in Progress**


"""


STEP_1_COMMENT = "🚀"
STEP_2_COMMENT = "🚀 The Project Refinement step has been completed. Please review the refinement and feel free to edit the page to your liking. To proceed to the next step, comment <strong>/next</strong>."
STEP_3_COMMENT = "🚀 You have completed the Output Structure Suggestion step. Please review and edit the structure to fit your needs, and choose between a simple or a detailed structure. You can proceed to the next step by commenting <strong>/next simple</strong> for a simple structure or <strong>/next detailed</strong> for a detailed structure."
STEP_4_COMMENT = "🚀 I have selected the best fitting agents for the project and derived specialized agents, please review and edit to your liking. Type <strong>/next</strong> to proceed!"
STEP_5_COMMENT = "🚀 All agents successfully created! Review the page generation instructions and agent assignment. Type <strong>/next</strong> to start the generation process!"
STEP_6_COMMENT = "🚀 Page Generation in Progress! In future versions of WikiAgents, you'll be able to refine project content directly from this page. For now, you can interact with individual pages."
