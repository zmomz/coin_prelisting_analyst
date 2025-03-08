import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from app.models.metric import Metric


async def get_latest_metrics(db: AsyncSession, coin_id: uuid.UUID) -> Dict[str, Any]:
    """Fetch the latest metrics for a specific coin."""
    result = await db.execute(
        select(Metric)
        .where(Metric.coin_id == coin_id, Metric.is_active == True)
        .order_by(Metric.fetched_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()
    return metric.__dict__ if metric else {}
