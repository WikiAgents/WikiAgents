# Copyright (C) [Year] [Your Name or Your Organization]
#
# This file is part of [Project Name].
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version, for non-commercial use only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# Educational and research institutions are exempt from the commercial license
# requirement and may use this software for internal, academic, and research
# purposes without the need for a commercial license.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/agpl-3.0.html>.
#
# For commercial use, a separate license is required. Contact [your-email@example.com]
# for more information.

import json
import ntpath
import os
import re
from datetime import datetime
from glob import glob

from bs4 import BeautifulSoup
from markdown import markdown as md2html
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from shared.agent_onboarding import AgentOnboarding
from shared.constants import *
from shared.models import AgentType, RedisAgent
from shared.utils import (
    extract_code,
    extract_section_content,
    markdown_list_to_list,
    parse_agent_markdown,
)
from shared.tools_redis_cache import ToolsRedisCache
from shared.utils import extract_code

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_DATABASE = os.environ["DB_DATABASE"]
DB_URL = f"mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@bookstack-db:3306/{DB_DATABASE}"

base_url = os.environ["APP_URL"]
token_id = os.environ["WA_TOKEN"]
token_secret = os.environ["WA_SECRET"]


engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)


Base = declarative_base()


class Bookshelf(Base):
    __tablename__ = "bookshelves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(180), nullable=False)
    slug = Column(String(180), nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_by = Column(Integer, nullable=True, index=True)
    updated_by = Column(Integer, nullable=True, index=True)
    image_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    owned_by = Column(Integer, nullable=False, index=True)
    description_html = Column(Text, nullable=False)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(191), nullable=False)
    slug = Column(String(191), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    image_id = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    owned_by = Column(Integer, nullable=False)
    default_template_id = Column(Integer, nullable=True)
    description_html = Column(Text, nullable=False)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False, index=True)
    slug = Column(String(191), nullable=False, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False, index=True)
    updated_by = Column(Integer, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    owned_by = Column(Integer, nullable=False, index=True)
    description_html = Column(Text, nullable=False)
    default_template_id = Column(Integer, nullable=True)


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, nullable=False, index=True)
    chapter_id = Column(Integer, nullable=False)
    name = Column(String(191), nullable=False)
    slug = Column(String(191), nullable=False)
    html = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=False)
    updated_by = Column(Integer, nullable=False)
    draft = Column(Boolean, nullable=False, default=False)
    markdown = Column(Text, nullable=True, default="")
    revision_count = Column(Integer, nullable=False)
    template = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    owned_by = Column(Integer, nullable=False)
    editor = Column(String(50), nullable=False)


class JointPermission(Base):
    __tablename__ = "joint_permissions"

    role_id = Column(Integer, nullable=False, primary_key=True)
    entity_type = Column(String(191), nullable=False, primary_key=True)
    entity_id = Column(Integer, nullable=False, primary_key=True)
    status = Column(Integer, nullable=False)
    owner_id = Column(Integer, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    entity_id = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(100), nullable=False)
    name = Column(String(191), nullable=False, index=True)
    value = Column(String(191), nullable=False, index=True)
    order = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


def md2text(markdown: str):
    html = md2html(markdown)
    html = re.sub(r"<pre>(.*?)</pre>", " ", html)
    html = re.sub(r"<code>(.*?)</code >", " ", html)
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(string=True))
    return text


def create_page(
    book_id: int,
    chapter_id: int,
    name: str,
    slug: str,
    is_template: bool,
    markdown: str,
):
    #     <pre id="bkmrk-import-wikipedia-def"><code class="language-python">import wikipedia

    # def search_wikipedia(topic: str):
    #     """
    #     Search on Wikipedia for a given topic. Returns relevant Wikipedia page titles.

    #     Args:
    #         topic (str): The topic to search for.

    #     Returns:
    #         List[str]: The list of page titles.
    #     """
    #     result = wikipedia.search(topic, results=20)
    #     return result
    # </code></pre>

    if markdown.startswith("```python"):
        code = extract_code(markdown)
        html = f'<pre><code class="language-python">{code}\n</code></pre>'
    else:
        html = md2html(markdown)
        html = html.replace("<p><code>json\n", '<pre><code class="language-json">')
        html = html.replace("</code></p>", "\n</code></pre>")
    page = Page(
        book_id=book_id,
        chapter_id=chapter_id,
        name=name,
        slug=slug,
        priority=2,
        created_by=3,
        updated_by=3,
        revision_count=1,
        template=1 if is_template else 0,
        owned_by=3,
        editor="markdown",
        markdown=markdown,
        html=html,
        text=md2text(markdown),
    )
    session.add(page)
    session.commit()
    session.refresh(page)
    for role_id in [1, 2, 3, 4]:
        session.add(
            JointPermission(
                role_id=role_id,
                entity_type="page",
                entity_id=page.id,
                status=1 if role_id > 1 else 3,
                owner_id=3,
            )
        )
    session.commit()
    return page


def create_chapter(book_id: int, name: str, slug: str, description: str):
    chapter = Chapter(
        book_id=book_id,
        name=name,
        slug=slug,
        description=description,
        priority=2,
        created_by=3,
        updated_by=3,
        owned_by=3,
        description_html=f"<p>{description}</p>",
    )
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    for role_id in [1, 2, 3, 4]:
        session.add(
            JointPermission(
                role_id=role_id,
                entity_type="chapter",
                entity_id=chapter.id,
                status=1 if role_id > 1 else 3,
                owner_id=3,
            )
        )
    session.commit()
    return chapter


def parse_creative_groups(base_path):
    groups = []
    try:
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                group_name = " ".join(
                    [
                        s.capitalize() if s[0].islower() else s
                        for s in folder_path.split("/")[-1].split("_")
                    ]
                )
                group = {"name": group_name}
                with open(folder_path + "/environment.md") as f:
                    environment = f.read()
                group["environment"] = environment
                group["persons"] = {}
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".md"):
                        file_path = os.path.join(folder_path, file_name)
                        if ntpath.basename(file_path)[:-3] == "environment":
                            continue
                        try:
                            with open(file_path, "r", encoding="utf-8") as md_file:
                                content = md_file.read()
                                name = " ".join(
                                    [
                                        s.capitalize() if s[0].islower() else s
                                        for s in ntpath.basename(file_path)[:-3].split(
                                            "_"
                                        )
                                    ]
                                )
                                group["persons"][name] = {"markdown": content}
                        except Exception as e:
                            print(f"Error reading file {file_name}: {e}")
                groups.append(group)
    except Exception as e:
        print(f"Error processing base path {base_path}: {e}")
    return groups


def parse_content_integrity(base_path):
    groups = []
    try:
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                group_name = " ".join(
                    [
                        s.capitalize() if s[0].islower() else s
                        for s in folder_path.split("/")[-1].split("_")
                    ]
                )
                group = {"name": group_name, "agents": {}}
                description = ""
                if os.path.exists(folder_path + "/description.md"):
                    with open(folder_path + "/description.md") as f:
                        description = f.read()
                group["description"] = description
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".md"):
                        file_path = os.path.join(folder_path, file_name)
                        if ntpath.basename(file_path)[:-3] == "description":
                            continue
                        try:
                            with open(file_path, "r", encoding="utf-8") as md_file:
                                content = md_file.read()
                                name = " ".join(
                                    [
                                        s.capitalize() if s[0].islower() else s
                                        for s in ntpath.basename(file_path)[:-3].split(
                                            "_"
                                        )
                                    ]
                                )
                                group["agents"][name] = {"markdown": content}
                        except Exception as e:
                            print(f"Error reading file {file_name}: {e}")
                groups.append(group)

    except Exception as e:
        print(f"Error processing base path {base_path}: {e}")
    return groups


def parse_content_task_agents(base_path):
    agents = {}
    for file_name in os.listdir(base_path):
        file_path = os.path.join(base_path, file_name)
        if os.path.isfile(file_path):
            if file_name.endswith(".md"):
                file_path = os.path.join(base_path, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as md_file:
                        content = md_file.read()
                        name = " ".join(
                            [
                                s.capitalize() if s[0].islower() else s
                                for s in ntpath.basename(file_path)[:-3].split("_")
                            ]
                        )
                        agents[name] = {"markdown": content}
                except Exception as e:
                    print(f"Error reading file {file_name}: {e}")
    return agents


def parse_tools(base_path):
    groups = []
    try:
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if os.path.isdir(folder_path):
                group_name = " ".join(
                    [
                        s.capitalize() if s[0].islower() else s
                        for s in folder_path.split("/")[-1].split("_")
                    ]
                )
                group = {"name": group_name, "tools": {}}
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(".md"):
                        file_path = os.path.join(folder_path, file_name)
                        try:
                            with open(file_path, "r", encoding="utf-8") as md_file:
                                content = md_file.read()
                                name = " ".join(
                                    [
                                        s.capitalize() if s[0].islower() else s
                                        for s in ntpath.basename(file_path)[:-3].split(
                                            "_"
                                        )
                                    ]
                                )
                                group["tools"][name] = {"markdown": content}
                        except Exception as e:
                            print(f"Error reading file {file_name}: {e}")
                groups.append(group)
    except Exception as e:
        print(f"Error processing base path {base_path}: {e}")
    return groups


shelves = [
    (
        "📚🧠Knowledge Bases",
        "knowledge-bases",
        "Knowledge Bases can be used to ground agents",
    )
]


with SessionLocal() as session:

    for shelve_name, slug, description in shelves:
        if not session.query(Bookshelf).filter_by(name=shelve_name).first():
            shelf = Bookshelf(
                name=shelve_name,
                slug=slug,
                description=description,
                created_by=3,
                updated_by=3,
                owned_by=3,
                description_html=f"<p>{description}</p>",
            )
            session.add(shelf)
            session.commit()
            session.refresh(shelf)
            for role_id in [1, 2, 3, 4]:
                session.add(
                    JointPermission(
                        role_id=role_id,
                        entity_type="bookshelf",
                        entity_id=shelf.id,
                        status=1 if role_id > 1 else 3,
                        owner_id=3,
                    )
                )
            session.commit()

    for book_name, slug, description in [
        (
            "✨🤖Content & Task Agents",
            "content-task-agents",
            "Available agents for content creation or task solving",
        ),
        ("🛠️🌐Tools", "tools", "Tools that agents can use to solve tasks"),
        (
            "🤹‍♀️💡Creative Feedback Groups",
            "creative-feedback-groups",
            "Creative Feedback Groups can brainstorm about your content and give you feedback from targeted perspectives.",
        ),
        (
            "✅🧠Content Integrity Agents",
            "content-integrity-agents",
            "Content Integrity Agents can review your content for factual mistakes, detect biases or check if it's in alignment with other definable documents.",
        ),
    ]:
        if not session.query(Book).filter_by(name=book_name, created_by=3).first():
            book = Book(
                name=book_name,
                slug=slug,
                description=description,
                created_by=3,
                updated_by=3,
                owned_by=3,
                description_html="",
            )
            session.add(book)
            session.commit()
            session.refresh(book)

            for role_id in [1, 2, 3, 4]:
                session.add(
                    JointPermission(
                        role_id=role_id,
                        entity_type="book",
                        entity_id=book.id,
                        status=1 if role_id > 1 else 3,
                        owner_id=3,
                    )
                )
            session.commit()

            if slug == "content-task-agents":
                with open("/custom_init/books/agent_template.md", "r") as f:
                    content = f.read()
                create_page(
                    book.id,
                    0,
                    "Agent Template",
                    "agent-template",
                    is_template=True,
                    markdown=content,
                )
                agents = parse_content_task_agents("/custom_init/books/content_task")
                for agent_name, agent in agents.items():
                    agent_slug = agent_name.lower().replace(" ", "-")
                    page = create_page(
                        book.id, 0, agent_name, agent_slug, False, agent["markdown"]
                    )
                    (
                        description,
                        code_path,
                        command,
                        parameters,
                        tools,
                    ) = parse_agent_markdown(agent["markdown"])
                    # tools = markdown_list_to_list(extract_code(extract_section_content(agent["markdown"], "##### Tools"))) #TODO

                    AgentOnboarding().onboard_agent(
                        RedisAgent(
                            name=agent_name,
                            description=description,
                            type="content_agent",
                            page_id=page.id,
                            code_path=code_path,
                            command=command,
                            parameters=parameters,
                        )
                    )

            elif slug == "content-integrity-agents":
                groups = parse_content_integrity("/custom_init/books/content_integrity")
                for g in groups:
                    name = g["name"]
                    chapter = create_chapter(
                        book.id,
                        name,
                        slug=name.replace(" ", "-").replace("_", "-"),
                        description=g["description"],
                    )
                    for agent_name, agent in g["agents"].items():
                        agent_slug = agent_name.lower().replace(" ", "-")
                        (
                            description,
                            code_path,
                            command,
                            parameters,
                            tools,
                        ) = parse_agent_markdown(agent["markdown"])
                        page = create_page(
                            book.id,
                            chapter.id,
                            agent_name,
                            agent_slug,
                            False,
                            agent["markdown"],
                        )
                        AgentOnboarding().onboard_agent(
                            RedisAgent(
                                name=agent_name,
                                description=description,
                                type="integrity_agent",
                                page_id=page.id,
                                code_path=code_path,
                                command=command,
                                parameters=parameters,
                                tools=tools,
                            )
                        )
                        for t in [
                            {"name": "Agent", "value": agent_name},
                            {"name": "Content Integrity Agent"},
                        ]:
                            tag = Tag(
                                entity_id=page.id,
                                entity_type="page",
                                name=t["name"],
                                value=t.get("value", ""),
                                order=0,
                            )
                            session.add(tag)
                        session.commit()

            elif slug == "creative-feedback-groups":
                groups = parse_creative_groups("/custom_init/books/creative_groups")
                for g in groups:
                    name = g["name"]
                    chapter = create_chapter(
                        book.id,
                        name,
                        slug=name.replace(" ", "-").replace("_", "-"),
                        description=g["environment"],
                    )
                    for agent_name, agent in g["persons"].items():
                        agent_name = agent_name.replace("lecun", "LeCun")
                        agent_slug = agent_name.lower().replace(" ", "-")
                        page = create_page(
                            book.id,
                            chapter.id,
                            agent_name,
                            agent_slug,
                            False,
                            agent["markdown"],
                        )
                        (
                            description,
                            code_path,
                            command,
                            parameters,
                            tools,
                        ) = parse_agent_markdown(agent["markdown"])
                        AgentOnboarding().onboard_agent(
                            RedisAgent(
                                name=agent_name,
                                type="creative_agent",
                                page_id=page.id,
                                description=description,
                                command=command,
                                code_path=code_path,
                                parameters=parameters,
                                tools=tools,
                            )
                        )
                        for t in [
                            {"name": "Agent", "value": agent_name},
                            {"name": "TinyTroupe"},
                        ]:
                            tag = Tag(
                                entity_id=page.id,
                                entity_type="page",
                                name=t["name"],
                                value=t.get("value", ""),
                                order=0,
                            )
                            session.add(tag)
                        session.commit()

            elif slug == "tools":
                groups = parse_tools("/custom_init/books/tools")
                for g in groups:
                    name = g["name"]
                    chapter = create_chapter(
                        book.id,
                        name,
                        slug=name.replace(" ", "-").replace("_", "-"),
                        description=" ",
                    )
                    for tool_name, tool in g["tools"].items():
                        tool_slug = tool_name.lower().replace(" ", "-")
                        page = create_page(
                            book.id,
                            chapter.id,
                            tool_name,
                            tool_slug,
                            False,
                            tool["markdown"],
                        )  #
                        code = extract_code(tool["markdown"])
                        updated, error = ToolsRedisCache().update_tool(
                            tool_name, tool_id=page.id, code=code
                        )
                        if updated:
                            print(f"Created Tool: {tool_name}")
                        else:
                            print(f"Unable to create Tool: {tool_name}")
