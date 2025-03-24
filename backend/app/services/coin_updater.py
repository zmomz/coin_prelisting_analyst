from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.crud.coins import get_coins, update_coin
from app.db.session import AsyncSessionLocal
from app.models import Metric
from app.schemas.coin import CoinUpdate
from app.utils.api_clients.coingecko import (
    fetch_and_store_coins,
    fetch_coin_market_data,
)


async def update_coin_list():
    """Pull all coins from CoinGecko and persist new ones."""
    async with AsyncSessionLocal() as db:
        await fetch_and_store_coins(db)


async def update_all_coin_metrics():
    """Fetch metrics for all active coins and store them."""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            coins = await get_coins(db)
            if not coins:
                return

            for coin in coins:
                market_data = await fetch_coin_market_data(coin.coingeckoid)
                if not market_data:
                    continue

                await update_coin(
                    db,
                    coin,
                    CoinUpdate(
                        description=market_data["description"],
                        github=market_data["github"],
                        x=market_data["x"],
                        reddit=market_data["reddit"],
                        telegram=market_data["telegram"],
                        website=market_data["website"],
                    ),
                )

                metrics = _process_coin_data(market_data)
                if not metrics:
                    continue

                db.add(
                    Metric(
                        coin_id=coin.id,
                        market_cap=metrics["market_cap"],
                        volume_24h=metrics["volume_24h"],
                        liquidity=metrics["liquidity"],
                        github_activity=metrics["github_activity"],
                        twitter_sentiment=metrics["twitter_sentiment"],
                        reddit_sentiment=metrics["reddit_sentiment"],
                        fetched_at=datetime.utcnow(),
                    )
                )

            await db.commit()

        except Exception:
            await db.rollback()
            raise
        finally:
            await engine.dispose()


def _process_coin_data(data: dict) -> dict | None:
    if not data:
        return None

    return {
        "market_cap": {"value": data.get("market_cap", 0), "currency": "USD"},
        "volume_24h": {"value": data.get("total_volume", 0), "currency": "USD"},
        "liquidity": {"value": data.get("liquidity_score", 0), "currency": "USD"},
        "github_activity": data.get("developer_data", {}).get(
            "commit_count_4_weeks", 0
        ),
        "twitter_sentiment": data.get("sentiment_votes_up_percentage", 0.0),
        "reddit_sentiment": data.get("sentiment_votes_down_percentage", 0.0),
    }
