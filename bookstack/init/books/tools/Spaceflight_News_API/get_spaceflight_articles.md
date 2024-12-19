```python 
import requests

BASE_URL = "https://api.spaceflightnewsapi.net/v4"

def get_latest_articles(limit=5):
    """
    Fetch the latest articles, sorted by publication date.
    
    Args:
        limit (int): The maximum number of latest articles to fetch (default is 5).
    
    Returns:
        dict: A dictionary containing the list of latest articles or an error message.
    """
    url = f"{BASE_URL}/articles"
    params = {"limit": limit, "sort": "-publishedAt"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

```   

