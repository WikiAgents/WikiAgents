# WikiAgents User Guide

## Create a New Project

1. **Navigate to the Projects Section**
   - Go to the **Projects** section.

2. **Create a New Project**
   - Click **New Project** in the right-side menu.
   - Set a project name and description, then click **Create**.

3. **Start the Interactive Project Wizard**
   - Go to **Metadata/Project Requirements** to begin the wizard.
     - **Step 1**: Review the initial project description. Assign creative agents and a grounding agent to ensure all generated content is grounded to configurable content from the knowledge bases. Type `/next` in the comments.
     ![Project Wizard Step 1](images/project_wizard_step_1.jpg)
     - **Step 2**: The system refines the description and identifies key components. Review, edit, and type `/next` to proceed.
     ![Project Wizard Step 2](images/project_wizard_step_2.jpg)
     - **Step 3**: The system generates a simple or detailed project output structure. Review, edit, and type `/next simple` or `/next detailed` to continue.
     ![Project Wizard Step 3](images/project_wizard_step_3.jpg)
     - **Step 4**: The system selects agents for the project and customizes agent parameters as needed. Type `/next` to initiate generation.
     ![Project Wizard Step 4](images/project_wizard_step_4.jpg)

4. **Review the Project Requirements Wizard Tape**
   - Verify all details and ensure the project setup aligns with your goals.
    ![Project Wizard Tape](images/project_wizard_tape.jpg)

5. **Optionally Run Agents**
   - Run **Integrity Agents** and/or **Creative Agents** on the entire project or specific pages as needed.
    ![Integrity Agents Showcase](images/integrity_agents.jpg)
    ![Creative Feedback Agents Showcase](images/creative_feedback_agents.jpg)
---

## Create New Content & Task Agents

### Customized Version of an Existing Agent

1. **Navigate to Content & Task Agents**
   - Open the **Content & Task Agents** section in the top menu.

2. **Select an Agent to Customize**
   - Go to the agent's page you want to modify.
   - Copy the content manually by editing the page, or click the **Copy** button in the right-side menu. You can copy to recently viewed chapters or books.

3. **Make Changes**
   - Adjust parameters or tools as needed.
   - Save the updated page.

### Custom Agent Code

1. **Set Up a New Folder**
   - Create a folder in the `agents/agents` path.

2. **Implement the Agent Code**
   - Subclass `WikiAgentBase` from `agents.base.agent`.
   - Ensure content-generating agents implement the `generate` function.

3. **Configure the Agent**
   - Use the `RedisAgent` parameter to access agents' wiki page configuration.
   - Use the `WikiContext` parameter to access the context about the wiki entity to generate.

4. **Create a New Agent Page**
   - Set the code path to your `WikiAgentBase` implementation (JSON format).
   - Define configurable parameters (JSON format).
   - Assign tools by referencing their names (tools must exist in the **Tools** section).

5. **Prepare the Environment**
   - Ensure all dependencies are available in the agent execution environment (defined in `agents/Dockerfile`).

---

## Create a New Content Integrity Agent

1. **Navigate to Content Integrity Agents**
   - Open the **Content Integrity Agents** section.
   - Create or copy a page for your new agent.

2. **Implement React Methods**
   - Integrity Agents are triggered by `/-commands` or natural language comments on pages.
   - Implement the `react_to_command` and/or `react_to_comment` methods from `WikiAgentBase` to handle these inputs.

---

## Create New Creative Feedback Agents

1. **Navigate to Creative Feedback Agents**
   - Open the **Creative Feedback Agents** section.
   - Create a page with a minimal description of the agent.

2. **Generate and Customize TinyPerson**
   - The system will automatically generate a **TinyPerson** and store a customization dump on the page.

3. **Assign to Projects**
   - Creative Feedback Agents can be assigned to projects and called using `/brainstorm <optional goal>` on a page.

4. **Organize Agents**
   - Group agents into chapters for easy retrieval and organization.

---

## Create a New Tool

1. **Navigate to the Tools Section**
   - Create a new page in the **Tools** section. The page name respresents the tool name.

2. **Implement the Tool**
   - Add a `json` section with the tool's code, or provide a detailed description of its intended functionality. The system will attempt to implement the tool based on the description.

3. **Prepare the Environment**
   - Ensure all dependencies are available in the agent execution environment (defined in `agents/Dockerfile`).

---

## Create a New Knowledge Base

1. **Navigate to the Knowledge Bases Section**
   - Go to the **Knowledge Bases** section in the top menu.

2. **Organize Knowledge**
   - Create **Books** and **Pages** to structure your knowledge effectively.

3. **Add Attachments**
   - Attach files or links to pages and use `/docling` to transcribe documents such as Word, Excel, PDFs, or websites.

4. **Schedule Website Transcriptions**
   - To periodically transcribe a website, use `/docling <interval in minutes>`.
