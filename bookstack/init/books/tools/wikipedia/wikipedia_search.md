```python
import wikipedia

@rate_limiter("Wikipedia", max_per_second=3, max_per_minute=60, max_per_hour=1000, timeout=60)
def search_wikipedia(topic: str, max_results: int):
    """
    Search on Wikipedia for a given topic. Returns relevant Wikipedia page titles.
    
    Args:
        topic (str): The topic to search for.
        max_results (int): The maximum number of results
    
    Returns:
        List[str]: The list of page titles.
    """
    result = wikipedia.search(topic, results=max_results)
    return result
```

