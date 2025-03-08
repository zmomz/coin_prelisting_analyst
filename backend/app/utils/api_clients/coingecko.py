import httpx
from app.core.config import settings
from typing import Optional, Dict


async def fetch_coin_market_data(symbol: str) -> Optional[Dict]:
    """Fetch market data for a given coin symbol from CoinGecko."""
    url = f"{settings.COINGECKO_API_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": symbol.lower(),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data:
            return None

        coin_data = data[0]
        return {
            "market_cap": coin_data.get("market_cap"),
            "volume_24h": coin_data.get("total_volume"),
            "liquidity": coin_data.get("liquidity_score"),
            "github": coin_data.get("repos_url", {}).get("github", [None])[0],  # Extract GitHub URL if available
        }
