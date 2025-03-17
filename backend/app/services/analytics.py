import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.models.metric import Metric


async def get_latest_metrics(db: AsyncSession, coin_id: uuid.UUID) -> Optional[dict]:
    """Fetch the latest metrics for a specific coin."""
    result = await db.execute(
        select(Metric)
        .where(Metric.coin_id == coin_id, Metric.is_active)
        .order_by(Metric.fetched_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()

    if metric:
        return {
            "id": metric.id,
            "coin_id": str(metric.coin_id),
            "fetched_at": metric.fetched_at,
            "values": metric.values,  # Adjust based on actual column names
        }
    
    return None
