import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric
from app.schemas.metric import MetricResponseSchema
from app.services.analytics import get_latest_metrics


@pytest.mark.asyncio(loop_scope="session")
async def get_latest_metrics(db: AsyncSession, coin_id):
    """Retrieve the latest metric for a given coin."""
    result = await db.execute(
        select(Metric)
        .where(Metric.coin_id == coin_id, Metric.is_active == True)
        .order_by(Metric.fetched_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()

    if not metric:
        return None  # No data found

    # ✅ Ensure we return a Pydantic model
    return MetricResponseSchema.model_validate(metric)
