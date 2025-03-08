import httpx
from typing import Optional, List, Dict
from app.core.config import settings


async def fetch_twitter_sentiment(twitter_handle: str) -> Optional[List[Dict]]:
    """Fetch recent tweets and analyze sentiment for a given Twitter handle."""
    if not twitter_handle:
        return None

    url = f"https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}
    params = {
        "query": f"from:{twitter_handle} -is:retweet",
        "max_results": 10,
        "tweet.fields": "created_at,public_metrics,text",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return None

        tweets = response.json().get("data", [])

        # Sentiment analysis placeholder (extend this with an actual NLP model)
        def analyze_sentiment(text):
            return "neutral"  # Stub, replace with real sentiment analysis

        return [
            {
                "text": tweet["text"],
                "sentiment": analyze_sentiment(tweet["text"]),
                "likes": tweet["public_metrics"]["like_count"],
                "retweets": tweet["public_metrics"]["retweet_count"],
                "created_at": tweet["created_at"],
            }
            for tweet in tweets
        ]
