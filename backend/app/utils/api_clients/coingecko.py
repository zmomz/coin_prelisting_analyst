import asyncio
import httpx
from typing import Optional, Dict
from app.core.config import settings


async def fetch_coin_market_data(symbol: str, retries: int = 5) -> Optional[Dict]:
    """Fetch market data for a given coin symbol from CoinGecko with retry logic."""
    url = f"{settings.COINGECKO_API_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": symbol.lower(),
    }

    delay = 1  # Initial delay for exponential backoff

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                if not data:
                    return None

                coin_data = data[0]
                return {
                    "coingeckoid": coin_data.get("id"),
                    "market_cap": {"value": coin_data.get("market_cap"), "currency": "USD"},
                    "volume_24h": {"value": coin_data.get("total_volume"), "currency": "USD"},
                    "liquidity": {"value": coin_data.get("liquidity_score"), "currency": "USD"},
                    "github_activity": coin_data.get("developer_data", {}).get("commit_count_4_weeks", 0),
                    "twitter_sentiment": coin_data.get("sentiment_votes_up_percentage", 0.0),
                    "reddit_sentiment": coin_data.get("sentiment_votes_down_percentage", 0.0),
                    "fetched_at": coin_data.get("last_updated"),
                }

            elif response.status_code == 429:
                print(f"⚠️ Rate limited. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    print("❌ Max retries exceeded for CoinGecko API")
    return None  # Return None if all retries fail
