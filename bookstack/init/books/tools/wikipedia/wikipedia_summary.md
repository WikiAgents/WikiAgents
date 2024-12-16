```python   
import wikipedia

@rate_limiter("Wikipedia", max_per_second=3, max_per_minute=60, max_per_hour=1000, timeout=60)
def wikipedia_summary(page_name: str):
    """
    Retrieves a summary of a Wikipedia page given its name. page_name must be a valid name returned by Wikipedia Search.
    
    Args:
        page_name (str): The Wikipedia page name
    
    Returns:
        str: The summary of the page
    """
    try:
        result = wikipedia.summary(page_name)
    except wikipedia.exceptions.DisambiguationError as e:
        return str(e)
    except wikipedia.exceptions.PageError as e:
        return str(e)
    return result
```

