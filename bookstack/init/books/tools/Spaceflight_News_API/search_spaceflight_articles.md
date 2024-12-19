```python 
import requests

BASE_URL = "https://api.spaceflightnewsapi.net/v4"

def search_articles(query, limit=10, offset=0):
    """
    Search for articles containing the given query string.
    
    Args:
        query (str): The search term to use.
        limit (int): The maximum number of articles to fetch (default is 10).
        offset (int): The number of articles to skip (default is 0).
    
    Returns:
        dict: A dictionary containing the list of matching articles or an error message.
    """
    url = f"{BASE_URL}/articles"
    params = {"search": query, "limit": limit, "offset": offset}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

```   





