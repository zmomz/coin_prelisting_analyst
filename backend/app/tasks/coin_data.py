from datetime import datetime
from app.models import Metric
from app.utils.api_clients.coingecko import fetch_coin_market_data, fetch_and_store_coins
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.celery_app import celery_app
from app.schemas.coin import CoinUpdate
from app.crud.coins import get_coins, update_coin
from app.db.session import AsyncSessionLocal
import asyncio
from app.core.config import settings
from sqlalchemy.orm import sessionmaker


@celery_app.task(name="app.tasks.coin_data.update_coins_list")
def update_coins_list():
    """Periodic task to update the list of coins in the database."""

    async def run_async_task():
        async with AsyncSessionLocal() as db_session:
            await fetch_and_store_coins(db_session)

    # Run async function inside a synchronous Celery task
    asyncio.run(run_async_task())

# coin_data.py
@celery_app.task(name="app.tasks.coin_data.fetch_coin_data")
def fetch_coin_data():
    """
    Celery must run sync tasks. We create an event loop 
    and execute the async function inside it.
    """
    try:
        asyncio.run(_fetch_coin_data_async())  # ✅ Correct way to run async function
    except Exception as e:
        print(f"❌ Error in fetch_coin_data: {e}")


async def _fetch_coin_data_async():
    """
    The actual async function that fetches market data and updates the DB.
    """
    # Create a fresh engine and session factory for this task execution
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as db_session:  # ✅ This ensures the session is created inside the current loop
        try:
            # Fetch active coins
            active_coins = await get_coins(db_session)
            print(f"⚙️ [fetch_coin_data] Fetched {len(active_coins)} coin(s).")

            if not active_coins:
                print("⚠️ No active coins found.")
                return

            # Process each coin
            for coin in active_coins:
                print(f"📡 Fetching market data for {coin.symbol} [Coingecko ID: {coin.coingeckoid}]")

                market_data = await fetch_coin_market_data(coin.coingeckoid)
                if not market_data:
                    print(f"⚠️ No market data available for {coin.symbol}")
                    continue
                
                newcoin = CoinUpdate(
                        description=market_data["description"],
                        github=market_data["github"],
                        x=market_data["x"],
                        reddit=market_data["reddit"],
                        telegram=market_data["telegram"],
                        website=market_data["website"],
                )
                await update_coin(db_session, coin, newcoin)

                metrics = process_coin_data(market_data)
                print(f"📊 Processed metrics for {coin.symbol}: {metrics}")

                if metrics:
                    metric_record = Metric(
                        coin_id=coin.id,
                        market_cap=metrics["market_cap"],
                        volume_24h=metrics["volume_24h"],
                        liquidity=metrics["liquidity"],
                        github_activity=metrics["github_activity"],
                        twitter_sentiment=metrics["twitter_sentiment"],
                        reddit_sentiment=metrics["reddit_sentiment"],
                        fetched_at=datetime.utcnow(),
                    )
                    db_session.add(metric_record)

            # ✅ COMMIT the session once after processing all coins
            await db_session.commit()
            print("✅ Market data fetching completed.")

        except Exception as e:
            print(f"❌ Error inside _fetch_coin_data_async: {e}")
            await db_session.rollback()  # Ensure rollback on failure
        finally:
            await engine.dispose()  # Properly dispose of the engine when done


def process_coin_data(market_data):
    """Process raw market data from CoinGecko and return structured metrics."""

    if not market_data:
        print("⚠️ No market data available")
        return None

    return {
        "market_cap": {"value": market_data.get("market_cap", 0), "currency": "USD"},
        "volume_24h": {"value": market_data.get("total_volume", 0), "currency": "USD"},
        "liquidity": {"value": market_data.get("liquidity_score", 0), "currency": "USD"},
        "github_activity": market_data.get("developer_data", {}).get("commit_count_4_weeks", 0),
        "twitter_sentiment": market_data.get("sentiment_votes_up_percentage", 0.0),
        "reddit_sentiment": market_data.get("sentiment_votes_down_percentage", 0.0),
    }

def fill_missing_data(market_data):
    if not market_data:
        print("⚠️ No market data available")
        return None
    return {
                    "symbol": coin_data.get("symbol"),
                    "description": coin_data.get("description", {}).get("en", ""),
                    "github": github_url,
                    "x": f"https://x.com/{coin_data.get('links', {}).get('twitter_screen_name', '')}",
                    "reddit": coin_data.get("links", {}).get("subreddit_url", ""),
                    "telegram": f"https://t.me/{coin_data.get('links', {}).get('telegram_channel_identifier', '')}",
                    "website": coin_data.get("links", {}).get("homepage", [""])[0],
                    "coingeckoid": coin_data.get("id"),
    }