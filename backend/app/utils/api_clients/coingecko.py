import asyncio
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from app.models import Coin


async def fetch_and_store_coins(db_session: AsyncSession):
    """Fetch all available coins from CoinGecko and store new ones in the database."""

    url = "https://api.coingecko.com/api/v3/coins/list"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            coins_data = response.json()

            if not coins_data:
                print("❌ No coins data fetched.")
                return

            print(f"✅ Fetched {len(coins_data)} coins from CoinGecko.")

            # Query existing coins in the database
            existing_coins = {
                coin.coingeckoid
                for coin in await db_session.execute(
                    text("SELECT coingeckoid FROM coins")
                )
            }

            new_coins = []
            for coin in coins_data:
                if coin["id"] not in existing_coins:
                    new_coins.append(
                        Coin(
                            name=coin["name"],
                            symbol=coin["symbol"].upper(),
                            coingeckoid=coin["id"],
                            created_at=datetime.now(),
                        )
                    )

            if new_coins:
                db_session.add_all(new_coins)
                await db_session.commit()
                print(f"✅ Added {len(new_coins)} new coins to the database.")
            else:
                print("⚡ No new coins found.")

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except httpx.RequestError as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


async def fetch_coin_market_data(coin_id: str, retries: int = 5) -> Optional[dict]:
    """Fetch market data for a given coin from CoinGecko with retry logic."""

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    delay = 1  # Initial delay for exponential backoff
    response = None

    for attempt in range(retries):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10)
                await response.raise_for_status()
                coin_data = await response.json()

                if not coin_data:
                    return None

                github_list = coin_data.get("links", {}).get("repos_url", {}).get(
                    "github"
                ) or [""]
                github_url = github_list[0] if github_list else ""

                return {
                    "name": coin_data.get("name"),
                    "symbol": coin_data.get("symbol"),
                    "description": coin_data.get("description", {}).get("en", ""),
                    "github": github_url,
                    "x": f"https://x.com/{coin_data.get('links', {}).get('twitter_screen_name', '')}",
                    "reddit": coin_data.get("links", {}).get("subreddit_url", ""),
                    "telegram": f"https://t.me/{coin_data.get('links', {}).get('telegram_channel_identifier', '')}",
                    "website": coin_data.get("links", {}).get("homepage", [""])[0],
                    "coingeckoid": coin_data.get("id"),
                    "market_cap": coin_data.get("market_data", {})
                    .get("market_cap", {})
                    .get("usd", 0),
                    "total_volume": coin_data.get("market_data", {})
                    .get("total_volume", {})
                    .get("usd", 0),
                    "liquidity_score": coin_data.get("liquidity_score", 0),
                    "developer_data": coin_data.get("developer_data", {}),
                    "sentiment_votes_up_percentage": coin_data.get(
                        "sentiment_votes_up_percentage", 0.0
                    ),
                    "sentiment_votes_down_percentage": coin_data.get(
                        "sentiment_votes_down_percentage", 0.0
                    ),
                }

            except httpx.HTTPStatusError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except httpx.RequestError as req_err:
                print(f"Request error occurred: {req_err}")
            except Exception as err:
                print(f"An error occurred: {err}")

            # Handle rate limits and retry logic
            if response and response.status_code == 429:
                print(
                    f"⚠️ Rate limited. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(delay)
                delay *= 2
            elif response:
                print(
                    f"⚠️ Error with status code {response.status_code}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})"
                )
                await asyncio.sleep(delay)
                delay *= 2

    print("❌ Max retries exceeded for CoinGecko API")
    return None
