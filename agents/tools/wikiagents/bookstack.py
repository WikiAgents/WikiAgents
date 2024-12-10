import os
from typing import Optional

import requests


class BookStackAPIClient:
    def __init__(self, agent_name: str):
        """
        Initialize the API client with a base URL and API token.
        """

        self.base_url = "http://bookstack"
        self.headers = {
            "Authorization": f"Token {token_id}:{token_secret}",
            "Content-Type": "application/json",
        }

    ### Books Endpoints

    def list_books(self):
        url = f"{self.base_url}/api/books"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def create_book(self, name, description=None, tags=None):
        url = f"{self.base_url}/api/books"
        data = {"name": name}
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        response = requests.post(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def get_book(self, book_id):
        url = f"{self.base_url}/api/books/{book_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def update_book(self, book_id, name=None, description=None, tags=None):
        url = f"{self.base_url}/api/books/{book_id}"
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        response = requests.put(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def delete_book(self, book_id):
        url = f"{self.base_url}/api/books/{book_id}"
        response = requests.delete(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def export_book(self, book_id, export_type):
        """
        Export a book. Export types: html, pdf, plaintext, markdown.
        """
        url = f"{self.base_url}/api/books/{book_id}/export/{export_type}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.content  # Returns the exported file content

    ### Chapters Endpoints

    def list_chapters(self):
        url = f"{self.base_url}/api/chapters"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def create_chapter(self, book_id, name, description=None, tags=None):
        url = f"{self.base_url}/api/chapters"
        data = {"book_id": book_id, "name": name}
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        response = requests.post(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def get_chapter(self, chapter_id):
        url = f"{self.base_url}/api/chapters/{chapter_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def update_chapter(self, chapter_id, name=None, description=None, tags=None):
        url = f"{self.base_url}/api/chapters/{chapter_id}"
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        response = requests.put(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def delete_chapter(self, chapter_id):
        url = f"{self.base_url}/api/chapters/{chapter_id}"
        response = requests.delete(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def export_chapter(self, chapter_id, export_type):
        """
        Export a chapter. Export types: html, pdf, plaintext, markdown.
        """
        url = f"{self.base_url}/api/chapters/{chapter_id}/export/{export_type}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.content

    ### Pages Endpoints

    def list_pages(self):
        url = f"{self.base_url}/api/pages"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def create_page(
        self,
        book_id=None,
        chapter_id=None,
        name=None,
        html=None,
        markdown=None,
        tags=None,
    ):
        url = f"{self.base_url}/api/pages"
        data = {"name": name}
        if book_id is not None:
            data["book_id"] = book_id
        if chapter_id is not None:
            data["chapter_id"] = chapter_id
        if html is not None:
            data["html"] = html
        if markdown is not None:
            data["markdown"] = markdown
        if tags is not None:
            data["tags"] = tags
        data["priority"] = 1
        print(data)
        response = requests.post(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def get_page(self, page_id):
        url = f"{self.base_url}/api/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def update_page(
        self,
        page_id,
        book_id=None,
        chapter_id=None,
        name=None,
        html=None,
        markdown=None,
        tags=None,
    ):
        url = f"{self.base_url}/api/pages/{page_id}"
        data = {}
        if book_id is not None:
            data["book_id"] = book_id
        if chapter_id is not None:
            data["chapter_id"] = chapter_id
        if name is not None:
            data["name"] = name
        if html is not None:
            data["html"] = html
        if markdown is not None:
            data["markdown"] = markdown
        if tags is not None:
            data["tags"] = tags
        response = requests.put(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def delete_page(self, page_id):
        url = f"{self.base_url}/api/pages/{page_id}"
        response = requests.delete(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def export_page(self, page_id, export_type):
        """
        Export a page. Export types: html, pdf, plaintext, markdown.
        """
        url = f"{self.base_url}/api/pages/{page_id}/export/{export_type}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.content

    ### Shelves Endpoints

    def list_shelves(self):
        url = f"{self.base_url}/api/shelves"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def create_shelf(self, name, description=None, books=None, tags=None):
        url = f"{self.base_url}/api/shelves"
        data = {"name": name}
        if description is not None:
            data["description"] = description
        if books is not None:
            data["books"] = books
        if tags is not None:
            data["tags"] = tags
        response = requests.post(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def get_shelf(self, shelf_id):
        url = f"{self.base_url}/api/shelves/{shelf_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def update_shelf(
        self, shelf_id, name=None, description=None, books=None, tags=None
    ):
        url = f"{self.base_url}/api/shelves/{shelf_id}"
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if books is not None:
            data["books"] = books
        if tags is not None:
            data["tags"] = tags
        response = requests.put(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def delete_shelf(self, shelf_id):
        url = f"{self.base_url}/api/shelves/{shelf_id}"
        response = requests.delete(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    # Comments

    def create_comment(self, text: str, page_id: int, parent_id: Optional[int] = None):
        url = f"{self.base_url}/wikiagents/comments"
        if not text.startswith("<p>"):
            text = f"<p>{text}</p>"
        print("create_comment2:", len(text))

        data = {"page_id": page_id, "html": text}
        if parent_id is not None:
            data["parent_id"] = parent_id
        response = requests.post(url, headers=self.headers, json=data)
        print("COMMENT CREATED!!!")
        print(data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()


base_url = os.environ["APP_URL"]
token_id = os.environ["WA_TOKEN"]
token_secret = os.environ["WA_SECRET"]

client = BookStackAPIClient(
    "http://bookstack", token_id=token_id, token_secret=token_secret
)


def list_books():
    """Retrieve a list of all books.

    Returns:
        list: A list of books with their details.
    """
    return client.list_books()


def create_book(
    name: str, description: Optional[str] = None, tags: Optional[list] = None
):
    """Create a new book.

    Args:
        name (str): Name of the book.
        description (str, optional): Description of the book.
        tags (list, optional): List of tags for the book.

    Returns:
        dict: Details of the created book.
    """
    return client.create_book(name=name, description=description, tags=tags)


def get_book(book_id: int):
    """Retrieve details of a specific book.

    Args:
        book_id (int): The ID of the book.

    Returns:
        dict: Details of the requested book.
    """
    return client.get_book(book_id=book_id)


def update_book(
    book_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list] = None,
):
    """Update details of a specific book.

    Args:
        book_id (int): The ID of the book.
        name (str, optional): New name for the book.
        description (str, optional): New description for the book.
        tags (list, optional): Updated tags for the book.

    Returns:
        dict: Details of the updated book.
    """
    return client.update_book(
        book_id=book_id, name=name, description=description, tags=tags
    )


def delete_book(book_id: int):
    """Delete a specific book.

    Args:
        book_id (int): The ID of the book to delete.

    Returns:
        dict: Details of the deletion status.
    """
    return client.delete_book(book_id=book_id)


def export_book(book_id: int, export_type: str):
    """Export a book in a specific format.

    Args:
        book_id (int): The ID of the book.
        export_type (str): The export format (html, pdf, plaintext, markdown).

    Returns:
        bytes: The exported file content.
    """
    return client.export_book(book_id=book_id, export_type=export_type)


def list_chapters():
    """Retrieve a list of all chapters.

    Returns:
        list: A list of chapters with their details.
    """
    return client.list_chapters()


def create_chapter(
    book_id: int,
    name: str,
    description: Optional[str] = None,
    tags: Optional[list] = None,
):
    """Create a new chapter.

    Args:
        book_id (int): The ID of the book to add the chapter to.
        name (str): Name of the chapter.
        description (str, optional): Description of the chapter.
        tags (list, optional): List of tags for the chapter.

    Returns:
        dict: Details of the created chapter.
    """
    return client.create_chapter(
        book_id=book_id, name=name, description=description, tags=tags
    )


def get_chapter(chapter_id: int):
    """Retrieve details of a specific chapter.

    Args:
        chapter_id (int): The ID of the chapter.

    Returns:
        dict: Details of the requested chapter.
    """
    return client.get_chapter(chapter_id=chapter_id)


def update_chapter(
    chapter_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[list] = None,
):
    """Update details of a specific chapter.

    Args:
        chapter_id (int): The ID of the chapter.
        name (str, optional): New name for the chapter.
        description (str, optional): New description for the chapter.
        tags (list, optional): Updated tags for the chapter.

    Returns:
        dict: Details of the updated chapter.
    """
    return client.update_chapter(
        chapter_id=chapter_id, name=name, description=description, tags=tags
    )


def delete_chapter(chapter_id: int):
    """Delete a specific chapter.

    Args:
        chapter_id (int): The ID of the chapter to delete.

    Returns:
        dict: Details of the deletion status.
    """
    return client.delete_chapter(chapter_id=chapter_id)


def export_chapter(chapter_id: int, export_type: str):
    """Export a chapter in a specific format.

    Args:
        chapter_id (int): The ID of the chapter.
        export_type (str): The export format (html, pdf, plaintext, markdown).

    Returns:
        bytes: The exported file content.
    """
    return client.export_chapter(chapter_id=chapter_id, export_type=export_type)


def list_pages():
    """Retrieve a list of all pages.

    Returns:
        list: A list of pages with their details.
    """
    return client.list_pages()


def create_page(
    book_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    name: Optional[str] = None,
    html: Optional[str] = None,
    markdown: Optional[str] = None,
    tags: Optional[list] = None,
):
    """Create a new page.

    Args:
        book_id (int, optional): The book ID to associate the page with.
        chapter_id (int, optional): The chapter ID to associate the page with.
        name (str, optional): Name of the page.
        html (str, optional): HTML content of the page.
        markdown (str, optional): Markdown content of the page.
        tags (list, optional): List of tags for the page.

    Returns:
        dict: Details of the created page.
    """
    return client.create_page(
        book_id=book_id,
        chapter_id=chapter_id,
        name=name,
        html=html,
        markdown=markdown,
        tags=tags,
    )


def get_page(page_id: int):
    """Retrieve details of a specific page.

    Args:
        page_id (int): The ID of the page.

    Returns:
        dict: Details of the requested page.
    """
    return client.get_page(page_id=page_id)


def update_page(
    page_id: int,
    book_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    name: Optional[str] = None,
    html: Optional[str] = None,
    markdown: Optional[str] = None,
    tags: Optional[list] = None,
):
    """Update details of a specific page.

    Args:
        page_id (int): The ID of the page.
        book_id (int, optional): Updated book ID to associate the page with.
        chapter_id (int, optional): Updated chapter ID to associate the page with.
        name (str, optional): New name for the page.
        html (str, optional): New HTML content for the page.
        markdown (str, optional): New Markdown content for the page.
        tags (list, optional): Updated tags for the page.

    Returns:
        dict: Details of the updated page.
    """
    return client.update_page(
        page_id=page_id,
        book_id=book_id,
        chapter_id=chapter_id,
        name=name,
        html=html,
        markdown=markdown,
        tags=tags,
    )


def delete_page(page_id: int):
    """Delete a specific page.

    Args:
        page_id (int): The ID of the page to delete.

    Returns:
        dict: Details of the deletion status.
    """
    return client.delete_page(page_id=page_id)


def export_page(page_id: int, export_type: str):
    """Export a page in a specific format.

    Args:
        page_id (int): The ID of the page.
        export_type (str): The export format (html, pdf, plaintext, markdown).

    Returns:
        bytes: The exported file content.
    """
    return client.export_page(page_id=page_id, export_type=export_type)


def list_shelves():
    """Retrieve a list of all shelves.

    Returns:
        list: A list of shelves with their details.
    """
    return client.list_shelves()


def create_shelf(
    name: str,
    description: Optional[str] = None,
    books: Optional[list] = None,
    tags: Optional[list] = None,
):
    """Create a new shelf.

    Args:
        name (str): Name of the shelf.
        description (str, optional): Description of the shelf.
        books (list, optional): List of book IDs to add to the shelf.
        tags (list, optional): List of tags for the shelf.

    Returns:
        dict: Details of the created shelf.
    """
    return client.create_shelf(
        name=name, description=description, books=books, tags=tags
    )


def get_shelf(shelf_id: int):
    """Retrieve details of a specific shelf.

    Args:
        shelf_id (int): The ID of the shelf.

    Returns:
        dict: Details of the requested shelf.
    """
    return client.get_shelf(shelf_id=shelf_id)


def update_shelf(
    shelf_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    books: Optional[list] = None,
    tags: Optional[list] = None,
):
    """Update details of a specific shelf.

    Args:
        shelf_id (int): The ID of the shelf.
        name (str, optional): New name for the shelf.
        description (str, optional): New description for the shelf.
        books (list, optional): Updated list of book IDs for the shelf.
        tags (list, optional): Updated tags for the shelf.

    Returns:
        dict: Details of the updated shelf.
    """
    return client.update_shelf(
        shelf_id=shelf_id, name=name, description=description, books=books, tags=tags
    )


def delete_shelf(shelf_id: int):
    """Delete a specific shelf.

    Args:
        shelf_id (int): The ID of the shelf to delete.

    Returns:
        dict: Details of the deletion status.
    """
    return client.delete_shelf(shelf_id=shelf_id)


def create_comment(text: str, page_id: int, reply_comment_id: Optional[int] = None):
    """Create a new comment or reply to an existing comment.

    Args:
        text (str): The content of the comment. Must be enclosed in <p> tags.
        page_id (int): The ID of the page to comment on.
        reply_comment_id (int, optional): The ID of the comment to reply to. If None, creates a new root comment.

    Returns:
        dict: Details of the created comment.
    """
    return client.create_comment(text=text, page_id=page_id, parent_id=reply_comment_id)


def get_book_content(book_id: int) -> str:
    """Get the content of a book given its' id.

    Args:
        book_id (int): Book ID

    Returns:
        str: The book content in markdown format.

    """
    # book = client.get_book(book_id)
    md = client.export_book(book_id, export_type="markdown")
    return md.decode()


def get_page_content(page_id: int) -> str:
    """Get the content of a page given its' id.

    Args:
        page_id (int): Page ID

    Returns:
        str: The page content in markdown format.

    """
    md = client.export_page(page_id, export_type="markdown")
    return md.decode()
