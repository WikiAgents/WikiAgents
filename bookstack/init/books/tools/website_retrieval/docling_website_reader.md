```python   
from docling.document_converter import DocumentConverter


@rate_limiter("Websites", max_per_second=2, max_per_minute=60, max_per_hour=1000, timeout=60)
def docling_website_reader(url: str):
    """
    Reads a website given its url. Returns the website content in markdown
    
    Args:
        url (str): The url to retrieve
    
    Returns:
        str: The content of the website in markdown
    """
    result = DocumentConverter().convert(url)
    return result.document.export_to_markdown()
```

