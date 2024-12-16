import base64
import json

from tapeagents.core import Tape

from agents.wikiagent.project_agent.tape import ProjectPlannerTape
from tapeagents.observe import retrieve_tape_llm_calls
from tapeagents.rendering import PrettyRenderer

from shared.bookstack_client import AgentBookStackClient
from shared.constants import (
    PROJECT_REQUIREMENTS_TAPE_PAGE_NAME,
    PAGE_CONTENT_GENERATION_TAPE_PAGE_NAME,
)
from shared.models import WikiContextInfo


def get_content_generation_tape(wiki_context: WikiContextInfo, tape_type: Tape):
    client = AgentBookStackClient("WikiAgent")
    tapes_chapter = client.get_chapter(wiki_context.project_context.tapes_chapter_id)
    tape = None
    tape_page_name = PAGE_CONTENT_GENERATION_TAPE_PAGE_NAME.format(
        page_id=wiki_context.page_id
    )

    tape_pages = [p for p in tapes_chapter["pages"] if p["name"] == tape_page_name]
    tape_page_exists = len(tape_pages) > 0
    if not tape_page_exists:
        return
    tape_page_id = tape_pages[0]
    attachments = client.get_attachments(page_id=tape_page_id)
    for attachment in attachments:
        if (
            attachment["name"] == f"page_{wiki_context.page_id}_gen_tape.json"
            and attachment["extension"] == "json"
        ):
            full_attachment = client.get_attachment(attachment["id"])
            tape_json = json.loads(base64.b64decode(full_attachment["content"]))
            tape = tape_type.model_validate(tape_json)
            break
    return tape


def save_content_generation_tape(wiki_context: WikiContextInfo, tape: Tape):
    tmp_filename = f"/tmp/page_{wiki_context.page_id}_gen_tape.json"
    with open(tmp_filename, "w") as f:
        json.dump(tape.model_dump(), f, indent=2)
    client = AgentBookStackClient("WikiAgent")
    tapes_chapter = client.get_chapter(wiki_context.project_context.tapes_chapter_id)
    tape_page_name = PAGE_CONTENT_GENERATION_TAPE_PAGE_NAME.format(
        page_id=wiki_context.page_id
    )
    tape_name = f"page_{wiki_context.page_id}_gen_tape.json"

    tape_pages = [p for p in tapes_chapter["pages"] if p["name"] == tape_page_name]
    tape_page_exists = len(tape_pages) > 0
    if tape_page_exists:
        page = tape_pages[0]
    else:
        page = client.create_page(
            book_id=wiki_context.project_context.metadata_book_id,
            chapter_id=tapes_chapter["id"],
            name=tape_page_name,
            html="Tape",
        )

    attachments = client.get_attachments(page_id=page["id"])
    attachment_exists = False
    for attachment in attachments:
        if attachment["name"] == tape_name and attachment["extension"] == "json":
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
