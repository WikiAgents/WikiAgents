```python
import wikipedia

def search_wikipedia(topic: str):
    """
    Search on Wikipedia for a given topic. Returns relevant Wikipedia page titles.
    
    Args:
        topic (str): The topic to search for.
    
    Returns:
        List[str]: The list of page titles.
    """
    result = wikipedia.search(topic, results=20)
    return result
```

