import time
import httpx
from typing import Any, Optional
from loguru import logger

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"


class SyncCoinGeckoClient:
    def __init__(self, base_url: str = COINGECKO_BASE_URL, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def get_coin_data(self, coin_id: str) -> Optional[dict[str, Any]]:
        """
        Fetch detailed data for a specific coin by its CoinGecko ID.
        Retries on 429 Too Many Requests and other temporary errors.
        """
        params = "?localization=false&tickers=false&market_data=true&"\
                 "community_data=true&developer_data=true&sparkline=false"

        url = f"{self.base_url}/coins/{coin_id.lower()}{params}"
        max_retries = 3
        delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429:
                    logger.warning(f"[{coin_id}] ⚠️ Rate limited (429). Attempt {attempt}/{max_retries}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(f"[{coin_id}] ❌ HTTP error {status}: {e}")
                    break
            except httpx.HTTPError as e:
                logger.error(f"[{coin_id}] ❌ Connection error: {e}")
                break

        logger.warning(f"[{coin_id}] 🚫 Failed after {max_retries} retries")
        return None

    def get_market_chart(self, coin_id: str, vs_currency: str = "usd", days: int = 30) -> Optional[dict[str, Any]]:
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days}
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"CoinGecko market chart error for '{coin_id}': {e}")
            return None

    def get_supported_coins(self) -> list[dict[str, Any]]:
        url = f"{self.base_url}/coins/list"
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"CoinGecko failed to fetch supported coins: {e}")
            return []

    def close(self):
        self.client.close()
