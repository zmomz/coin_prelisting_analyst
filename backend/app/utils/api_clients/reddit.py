from typing import Optional

import httpx

from app.core.config import settings


async def fetch_reddit_sentiment(subreddit: str) -> Optional[list[dict]]:
    """Fetch recent Reddit posts from a given subreddit and analyze sentiment."""
    if not subreddit:
        return None

    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=10"
    headers = {"User-Agent": settings.REDDIT_USER_AGENT}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            return None

        posts = response.json().get("data", {}).get("children", [])

        # Sentiment analysis placeholder (extend with NLP)
        def analyze_sentiment(text):
            return "neutral"  # Stub, replace with real sentiment analysis

        return [
            {
                "title": post["data"]["title"],
                "sentiment": analyze_sentiment(post["data"]["title"]),
                "upvotes": post["data"]["ups"],
                "comments": post["data"]["num_comments"],
                "created_at": post["data"]["created_utc"],
            }
            for post in posts
        ]
