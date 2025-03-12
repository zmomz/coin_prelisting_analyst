from sqlalchemy import text
from app.celery_app import celery_app
from app.db.session import AsyncSessionLocalMain
from app.utils.api_clients.coingecko import fetch_coin_market_data
from app.crud.metrics import create_metric
from app.schemas.metric import MetricCreate, MetricValueSchema


@celery_app.task(name="fetch_coin_data")
async def fetch_coin_data():
    """Fetches market data for all tracked coins and stores metrics."""
    async with AsyncSessionLocalMain() as db:
        coins = await db.execute(text("""
            SELECT id, symbol FROM coins WHERE is_active = true
        """))
        coins = coins.fetchall()

        for coin_id, symbol in coins:
            market_data = await fetch_coin_market_data(symbol)
            if market_data:
                metric_entry = MetricCreate(
                    coin_id=coin_id,
                    market_cap=MetricValueSchema(**market_data["market_cap"]),
                    volume_24h=MetricValueSchema(**market_data["volume_24h"]),
                    liquidity=MetricValueSchema(**market_data["liquidity"]),
                    github_activity=market_data["github_activity"],
                    twitter_sentiment=market_data["twitter_sentiment"],
                    reddit_sentiment=market_data["reddit_sentiment"],
                    fetched_at=market_data["fetched_at"]
                )
                await create_metric(db, metric_entry)
