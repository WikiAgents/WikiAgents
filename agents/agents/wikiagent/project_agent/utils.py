import base64
import json

from agents.wikiagent.project_agent.tape import ProjectPlannerTape
from tapeagents.observe import retrieve_tape_llm_calls
from tapeagents.rendering import PrettyRenderer

from shared.bookstack_client import AgentBookStackClient
from shared.constants import PROJECT_REQUIREMENTS_TAPE_PAGE_NAME
from shared.models import WikiContextInfo


def get_project_requirements_tape(wiki_context: WikiContextInfo):
    client = AgentBookStackClient("WikiAgent")
    tapes_chapter = client.get_chapter(wiki_context.project_context.tapes_chapter_id)
    tape = None
    for page in tapes_chapter["pages"]:
        if page["name"] == PROJECT_REQUIREMENTS_TAPE_PAGE_NAME:
            attachments = client.get_attachments(page_id=page["id"])
            for attachment in attachments:
                if (
                    attachment["name"]
                    == f"project_{wiki_context.project_id}_requirements_tape.json"
                    and attachment["extension"] == "json"
                ):
                    full_attachment = client.get_attachment(attachment["id"])
                    tape_json = json.loads(base64.b64decode(full_attachment["content"]))
                    tape = ProjectPlannerTape.model_validate(tape_json)
                    break
        if tape is not None:
            break
    return tape


def save_project_requirements_tape(
    wiki_context: WikiContextInfo, tape: ProjectPlannerTape
):
    tmp_filename = f"/tmp/project_{wiki_context.project_id}_requirements_tape.json"
    with open(tmp_filename, "w") as f:
        json.dump(tape.model_dump(), f, indent=2)
    client = AgentBookStackClient("WikiAgent")
    tapes_chapter = client.get_chapter(wiki_context.project_context.tapes_chapter_id)
    tape_name = f"project_{wiki_context.project_id}_requirements_tape.json"
    for page in tapes_chapter["pages"]:
        if page["name"] == PROJECT_REQUIREMENTS_TAPE_PAGE_NAME:
            attachments = client.get_attachments(page_id=page["id"])
            attachment_exists = False
            for attachment in attachments:
                if (
                    attachment["name"] == tape_name
                    and attachment["extension"] == "json"
                ):
                    client.update_attachment(
                        attachment_id=attachment["id"],
                        name=tape_name,
                        uploaded_to=page["id"],
                        file=tmp_filename,
                    )
                    attachment_exists = True
                    break
            if not attachment_exists:
                client.create_attachment(
                    name=tape_name, uploaded_to=page["id"], file=tmp_filename
                )

            renderer = PrettyRenderer()
            llm_calls = retrieve_tape_llm_calls(tape)
            rendered_tape = renderer.style + renderer.render_tape(tape, llm_calls)
            client.update_page(page["id"], html=rendered_tape)
            if "Tape" not in [
                a["name"] for a in client.get_attachments(page_id=wiki_context.page_id)
            ]:
                client.create_attachment(
                    "Tape", uploaded_to=wiki_context.page_id, link=f"/link/{page['id']}"
                )
            break


def update_tape_step(wiki_context: WikiContextInfo, step_index: int, update: dict):
    tape = get_project_requirements_tape(wiki_context)
    for k, v in update.items():
        setattr(tape[step_index], k, v)
    save_project_requirements_tape(wiki_context, tape)
