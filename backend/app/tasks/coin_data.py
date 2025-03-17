from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.models import Metric
from app.utils.api_clients.coingecko import fetch_coin_market_data
from app.celery_app import celery_app


@celery_app.task(name="app.tasks.coin_data.fetch_coin_data")
async def fetch_coin_data(db_session: AsyncSession):
    """Fetch market data for all active coins and store them in the database."""
    active_coins = await db_session.execute(
        text("SELECT id, symbol FROM coins WHERE is_active = true")
    )
    active_coins = active_coins.fetchall()

    print(f"🔍 Active coins: {active_coins}")

    for coin_id, symbol in active_coins:
        print(f"📡 Fetching market data for {symbol}")
        market_data = await fetch_coin_market_data(symbol)

        if not market_data:
            print(f"⚠️ No data for {symbol}")
            continue

        metrics = process_coin_data(market_data)
        print(f"📊 Processed metrics for {symbol}: {metrics}")

        if metrics:
            metric_record = Metric(
                coin_id=coin_id,
                market_cap=metrics["market_cap"],
                volume_24h=metrics["volume_24h"],
                liquidity=metrics["liquidity"],
                github_activity=metrics["github_activity"],
                twitter_sentiment=metrics["twitter_sentiment"],
                reddit_sentiment=metrics["reddit_sentiment"],
                fetched_at=datetime.utcnow()
            )
            db_session.add(metric_record)

    await db_session.commit()  # ✅ Ensure all data is saved


def process_coin_data(market_data):
    """Process raw market data from CoinGecko and return structured metrics."""
    if not market_data:
        print("⚠️ No market data available")
        return None

    return {
        "market_cap": market_data.get("market_cap", {"value": 0, "currency": "USD"}),
        "volume_24h": market_data.get("volume_24h", {"value": 0, "currency": "USD"}),
        "liquidity": market_data.get("liquidity", {"value": 0, "currency": "USD"}),
        "github_activity": market_data.get("github_activity", 0),
        "twitter_sentiment": market_data.get("twitter_sentiment", 0.0),
        "reddit_sentiment": market_data.get("reddit_sentiment", 0.0)
    }
