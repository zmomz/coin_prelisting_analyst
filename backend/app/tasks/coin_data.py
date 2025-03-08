import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.utils.api_clients.coingecko import fetch_coin_market_data
from app.crud.coins import get_coin_by_symbol
from app.crud.metrics import create_metric
from app.schemas.metric import MetricCreate


@celery_app.task(name="fetch_coin_data")
async def fetch_coin_data():
    """Fetches market data for all tracked coins and stores metrics."""
    async with AsyncSessionLocal() as db:
        coins = await db.execute("SELECT symbol, id FROM coins WHERE is_active = true")
        coins = coins.fetchall()

        for symbol, coin_id in coins:
            market_data = await fetch_coin_market_data(symbol)
            if market_data:
                metric_entry = MetricCreate(coin_id=coin_id, **market_data)
                await create_metric(db, metric_entry)
