```python   
import wikipedia

def wikipedia_summary(page_name: str):
    """
    Retrieves a summary of a Wikipedia page given its name.
    
    Args:
        page_name (str): The Wikipedia page name
    
    Returns:
        str: The summary of the page
    """
    result = wikipedia.summary(page_name)
    return result
```

