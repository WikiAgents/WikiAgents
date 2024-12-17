import os
from typing import Optional

import requests
from redis import Redis

redis = Redis("redis")


class BookStackAPIClient:
    def __init__(self, base_url: str, token_id: str, token_secret: str):
        """
        Initialize the API client with a base URL and API token.
        """
        self.base_url = base_url
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

    def create_chapter(self, book_id, name, description=None, tags=None, priority=None):
        url = f"{self.base_url}/api/chapters"
        data = {"book_id": book_id, "name": name}
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        if priority is not None:
            data["priority"] = priority
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

    def list_pages(self, book_id: int = None):
        url = f"{self.base_url}/api/pages"
        params = {}
        if book_id is not None:
            params["filter[book_id]"] = book_id
        response = requests.get(url, headers=self.headers, params=params)
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
        priority=None,
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
        if priority is not None:
            data["priority"] = priority
        else:
            data["priority"] = 1
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
        data = {"page_id": page_id, "html": text}
        if parent_id is not None:
            data["parent_id"] = parent_id
        response = requests.post(url, headers=self.headers, json=data)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def is_agent(self, user_id: int):
        url = f"{self.base_url}/api/users/{user_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()["email"].endswith("wikiagents.local")

    def book_project_membership(self, book_id: int):
        url = f"{self.base_url}/wikiagents/book_project_membership/{book_id}"
        response = requests.get(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()
        return response.json()

    def delete_user(self, user_id: int):
        url = f"{self.base_url}/api/users/{user_id}"
        response = requests.delete(url, headers=self.headers)
        if not response.ok:
            print(response.content)
            response.raise_for_status()

    def create_attachment(
        self, name: str, uploaded_to: int, file: str = None, link: str = None
    ):
        """
        Create a new attachment in the BookStack system.

        Args:
            name (str): The name of the attachment (required).
            uploaded_to (int): The ID of the page this attachment is related to (required).
            file (str, optional): The path to the file to upload (required if link is not provided).
            link (str, optional): A URL to associate as the attachment (required if file is not provided).

        Returns:
            dict: The response JSON if the request is successful.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/attachments"

        # Prepare data for the request
        data = {
            "name": name,
            "uploaded_to": uploaded_to,
        }

        # Check if either file or link is provided
        if file:
            # Use multipart/form-data for file upload
            with open(file, "rb") as f:
                files = {"file": (file, f)}
                for k, v in data.items():
                    files[k] = (None, v)
                headers = self.headers.copy()
                headers.pop("Content-Type")
                response = requests.post(url, headers=headers, files=files)
        elif link:
            # Send data as JSON for link-based attachment
            data["link"] = link
            response = requests.post(url, headers=self.headers, json=data)
        else:
            raise ValueError("Either 'file' or 'link' must be provided.")

        # Handle response
        if not response.ok:
            print(response.content)
            response.raise_for_status()

        return response.json()

    def get_attachment(self, attachment_id: int):
        """
        Retrieve details and content of a specific attachment by its ID.

        Args:
            attachment_id (int): The ID of the attachment to retrieve.

        Returns:
            dict: The response JSON containing attachment details and content.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/attachments/{attachment_id}"
        response = requests.get(url, headers=self.headers)

        # Handle response
        if not response.ok:
            print(response.content)
            response.raise_for_status()

        return response.json()

    def get_attachments(self, page_id: int = None):
        """
        Retrieve a list of attachments, optionally filtered by a specific page ID.

        Args:
            page_id (int, optional): The ID of the page to filter attachments by.

        Returns:
            list: A list of attachments.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/attachments"

        # Add filtering by page ID if provided
        params = {}
        if page_id is not None:
            params["filter[uploaded_to]"] = page_id

        response = requests.get(url, headers=self.headers, params=params)

        # Handle response
        if not response.ok:
            print(response.content)
            response.raise_for_status()

        return response.json()["data"]

    def update_attachment(
        self,
        attachment_id: int,
        name: str = None,
        uploaded_to: int = None,
        file: str = None,
        link: str = None,
    ):
        """
        Update the details of an existing attachment.

        Args:
            attachment_id (int): The ID of the attachment to update.
            name (str, optional): The new name of the attachment.
            uploaded_to (int, optional): The ID of the page this attachment should be related to.
            file (str, optional): The path to a new file to upload for the attachment.
            link (str, optional): A new URL to associate as the attachment.

        Returns:
            dict: The response JSON if the request is successful.

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/attachments/{attachment_id}"

        # Validate input
        if not (name or uploaded_to or file or link):
            raise ValueError(
                "At least one parameter (name, uploaded_to, file, or link) must be provided."
            )

        # Prepare data
        data = {}
        if name:
            data["name"] = name
        if uploaded_to:
            data["uploaded_to"] = uploaded_to
        if link:
            data["link"] = link

        # Determine request type based on file/link presence
        if file:
            with open(file, "rb") as f:
                files = {"file": (file, f), "_method": (None, "PUT")}
                for k, v in data.items():
                    files[k] = (None, v)
                headers = self.headers.copy()
                headers.pop("Content-Type")
                response = requests.post(url, headers=headers, files=files)
        elif link:
            # Include link in data and send as JSON
            data["link"] = link
            response = requests.put(url, headers=self.headers, json=data)
        else:
            # Send the rest of the data as JSON if no file or link is provided
            response = requests.put(url, headers=self.headers, json=data)

        # Handle response
        if not response.ok:
            print(response.content)
            response.raise_for_status()

        return response.json()

    def delete_attachment(self, attachment_id: int):
        """
        Delete an attachment by its ID.

        Args:
            attachment_id (int): The ID of the attachment to delete.

        Returns:
            None

        Raises:
            HTTPError: If the API request fails.
        """
        url = f"{self.base_url}/api/attachments/{attachment_id}"
        response = requests.delete(url, headers=self.headers)

        # Handle response
        if not response.ok:
            print(response.content)
            response.raise_for_status()


class AgentBookStackClient(BookStackAPIClient):
    def __init__(self, agent_name: str):
        token_id, token_secret = redis.hmget(
            f"agent:{agent_name}", ["token_id", "token_secret"]
        )
        try:
            super().__init__(
                "http://bookstack", token_id.decode(), token_secret.decode()
            )
        except:
            print("agent:", agent_name)
            raise
