```python   
import requests

def fetch_top_stories(limit=10):
    """
    Fetches the top stories from Hacker News and returns their titles, URLs, and scores.
    
    Args:
        limit (int, optional): The maximum number of stories to fetch. Defaults to 10.

    Returns:
        list: A list of dictionaries containing the title, URL, and score of the top stories.
    """
    # URL to fetch top story IDs
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

    try:
        # Fetch the top story IDs
        response = requests.get(top_stories_url)
        response.raise_for_status()
        top_story_ids = response.json()

        # Apply limit if specified
        if limit is not None:
            top_story_ids = top_story_ids[:limit]

        # Initialize a list to hold story details
        stories = []

        # Fetch details for each story ID
        for story_id in top_story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story_response = requests.get(story_url)
            story_response.raise_for_status()
            story_details = story_response.json()

            # Extract only the required fields
            stories.append({
                "title": story_details.get("title"),
                "url": story_details.get("url"),
                "score": story_details.get("score")
            })

        return stories

    except requests.RequestException as e:
        print(f"An error occurred while fetching top stories: {e}")
        return []
```

