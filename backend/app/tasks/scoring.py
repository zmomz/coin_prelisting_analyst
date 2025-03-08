import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.scoring import update_coin_score
from app.services.analytics import get_latest_metrics
from app.crud.coins import get_coins


@celery_app.task(name="recalculate_scores")
async def recalculate_scores():
    """Recalculates scores for all active coins."""
    async with AsyncSessionLocal() as db:
        coins = await get_coins(db)

        for coin in coins:
            metrics = await get_latest_metrics(db, coin.id)
            if metrics:
                await update_coin_score(db, coin.id, metrics)
