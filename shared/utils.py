import json
import re
from typing import List

from redis import Redis

from shared.bookstack_client import AgentBookStackClient
from shared.constants import *


def get_project_metadata_for_page(page_id: int):
    client = AgentBookStackClient("WikiAgent")
    page = client.get_page(page_id)
    projects = client.book_project_membership(page["book_id"])
    project_id = None
    project_name = None
    metadata_book = None
    involved_agents, involved_agents_chapter_id = [], None
    creative_agents, creative_agents_chapter_id = [], None
    integrity_agents, integrity_agents_chapter_id = [], None
    tapes, tapes_chapter_id = [], None
    for p in projects:
        for b in client.get_shelf(p["id"]).get("books", []):
            if b["name"] == PROJECT_METADATA_BOOK_NAME:
                metadata_book = b
                project_id = p["id"]
                project_name = p["name"]
                for page in client.get_book(b["id"])["contents"]:
                    if page["name"] == PROJECT_CREATIVE_FEEDBACK_CHAPTER_NAME:
                        creative_agents_chapter = client.get_chapter(page["id"])
                        creative_agents_chapter_id = creative_agents_chapter["id"]
                        creative_agents = creative_agents_chapter["pages"]
                    elif page["name"] == PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_NAME:
                        # integrity_agents = client.get_chapter(p["id"])["pages"]
                        integrity_agents_chapter = client.get_chapter(page["id"])
                        integrity_agents_chapter_id = integrity_agents_chapter["id"]
                        integrity_agents = integrity_agents_chapter["pages"]
                    elif page["name"] == PROJECT_AGENTS_CHAPTER_NAME:
                        # involved_agents = client.get_chapter(p["id"])["pages"]
                        involved_agents_chapter = client.get_chapter(page["id"])
                        involved_agents_chapter_id = involved_agents_chapter["id"]
                        involved_agents = involved_agents_chapter["pages"]
                    elif page["name"] == PROJECT_TAPES_CHAPTER_NAME:
                        tapes_chapter = client.get_chapter(page["id"])
                        tapes_chapter_id = tapes_chapter["id"]
                        tapes = tapes_chapter["pages"]

                break
        if metadata_book is not None:
            break
    metadata = {
        "project_id": project_id,
        "project_name": project_name,
        "metadata_book": metadata_book,
        "creative_agents": {
            "chapter_id": creative_agents_chapter_id,
            "pages": creative_agents,
        },
        "integrity_agents": {
            "chapter_id": integrity_agents_chapter_id,
            "pages": integrity_agents,
        },
        "involved_agents": {
            "chapter_id": involved_agents_chapter_id,
            "pages": involved_agents,
        },
        "tapes": {"chapter_id": tapes_chapter_id, "pages": tapes},
    }
    return metadata if metadata["metadata_book"] else None


# quick and dirty, merge with function above later.
def get_metadata_for_project_id(project_id: int):
    client = AgentBookStackClient("WikiAgent")
    metadata_book = None
    involved_agents, involved_agents_chapter_id = [], None
    creative_agents, creative_agents_chapter_id = [], None
    integrity_agents, integrity_agents_chapter_id = [], None
    tapes, tapes_chapter_id = [], None
    for b in client.get_shelf(project_id).get("books", []):
        if b["name"] == PROJECT_METADATA_BOOK_NAME:
            metadata_book = b
            for page in client.get_book(b["id"])["contents"]:
                if page["name"] == PROJECT_CREATIVE_FEEDBACK_CHAPTER_NAME:
                    creative_agents_chapter = client.get_chapter(page["id"])
                    creative_agents_chapter_id = creative_agents_chapter["id"]
                    creative_agents = creative_agents_chapter["pages"]
                elif page["name"] == PROJECT_CONTENT_INTEGRITY_AGENTS_CHAPTER_NAME:
                    integrity_agents_chapter = client.get_chapter(page["id"])
                    integrity_agents_chapter_id = integrity_agents_chapter["id"]
                    integrity_agents = integrity_agents_chapter["pages"]
                elif page["name"] == PROJECT_AGENTS_CHAPTER_NAME:
                    involved_agents_chapter = client.get_chapter(page["id"])
                    involved_agents_chapter_id = involved_agents_chapter["id"]
                    involved_agents = involved_agents_chapter["pages"]
                elif page["name"] == PROJECT_TAPES_CHAPTER_NAME:
                    tapes_chapter = client.get_chapter(page["id"])
                    tapes_chapter_id = tapes_chapter["id"]
                    tapes = tapes_chapter["pages"]

            break
        if metadata_book is not None:
            break
    metadata = {
        "project_id": project_id,
        "project_name": None,
        "metadata_book": metadata_book,
        "creative_agents": {
            "chapter_id": creative_agents_chapter_id,
            "pages": creative_agents,
        },
        "integrity_agents": {
            "chapter_id": integrity_agents_chapter_id,
            "pages": integrity_agents,
        },
        "involved_agents": {
            "chapter_id": involved_agents_chapter_id,
            "pages": involved_agents,
        },
        "tapes": {"chapter_id": tapes_chapter_id, "pages": tapes},
    }
    return metadata if metadata["metadata_book"] else None


import re


def extract_section_content(markdown: str, heading: str) -> dict:
    """
    Extracts the content between a given heading and the next "---" separator in the markdown.

    Args:
        markdown (str): The markdown string.
        heading (str): The heading to search for.

    Returns:
        dict: A dictionary with the heading as the key and the extracted content as the value.
    """
    # Escape special regex characters in the heading to avoid mismatches
    escaped_heading = re.escape(heading)

    # Pattern to find the heading and capture content until the next "---"
    pattern = rf"{escaped_heading}\s*(.*?)(?=\n---)"

    # Search using re.DOTALL to include multiline content
    match = re.search(pattern, markdown, re.DOTALL)

    if match:
        content = match.group(1).strip()
        return content
    return None


def extract_code(text: str) -> str:
    """
    Return only content inside the first pair of triple backticks if they are present.
    """
    if text is None:
        return
    tiks_counter = 0
    lines = text.strip().split("\n")
    clean_lines = []
    for line in lines:
        if line.startswith("```"):
            tiks_counter += 1
            if tiks_counter == 1:
                clean_lines = []
            elif tiks_counter == 2:
                break
            continue
        clean_lines.append(line) if tiks_counter > 0 else None
    return "\n".join(clean_lines) if len(clean_lines) > 0 else None


def markdown_list_to_list(markdown: str):
    result = []
    lines = markdown.splitlines()
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith(("- ", "* ", "+ ")):
            result.append(stripped_line[2:].strip())
    return result


def parse_agent_markdown(markdown: str):
    description = extract_section_content(markdown, "##### Description")
    code_path = extract_code(extract_section_content(markdown, "##### Code Path"))
    if code_path:
        code_path = json.loads(code_path)
    command = extract_code(extract_section_content(markdown, "##### Command"))
    if command:
        command = json.loads(command)
    parameters = extract_code(extract_section_content(markdown, "##### Parameters"))
    if parameters:
        parameters = json.loads(parameters)
    tools = extract_code(extract_section_content(markdown, "##### Tools"))
    if tools:
        tools = json.loads(tools)
    return description, code_path, command, parameters, tools


def flatten_list(nested_list):
    """
    Flattens a nested list into a single list.

    Parameters:
        nested_list (list): A list which may contain nested lists.

    Returns:
        list: A flattened list.
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            # Recursively flatten the nested list
            flattened.extend(flatten_list(item))
        else:
            # Append non-list items directly
            flattened.append(item)
    return flattened


from shared.models import RedisAgent


def get_llm(agent: RedisAgent):
    from tapeagents.llms import LiteLLM

    llm_params = {}
    if "llm_temperature" in agent.parameters:
        llm_params["temperature"] = agent.parameters["llm_temperature"]
    return LiteLLM(
        model_name=agent.parameters.get("llm", DEFAULT_LLM), parameters=llm_params
    )
