```python
import wikipedia
import time


@rate_limiter("Wikipedia", max_per_second=2, max_per_minute=30, max_per_hour=1000, timeout=60)
def search_wikipedia(query: str, max_results: int):
    """
    Search on Wikipedia given a query.
    
    Args:
        query (str): The query to search for.
        max_results (int): The maximum number of results
    
    Returns:
        str: The list of page titles.
    """
    results = wikipedia.search(query, results=max_results)
    summaries = []
    for title in results:
        if page := get_page(title):
            summaries.append(f"Page: {page.title} \nSummary: {page.summary}")
    return "\n".join(summaries)

def get_page(title):
    page = None
    try:
        page = wikipedia.page(title)
        time.sleep(0.1)
    except wikipedia.exceptions.PageError as e:
        pass
    except wikipedia.exceptions.DisambiguationError as e:
        pass
    return page

```
