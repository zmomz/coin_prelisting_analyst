import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric
from app.schemas.metric import MetricOut


@pytest.mark.asyncio(loop_scope="session")
async def test_get_latest_metrics(db_session: AsyncSession, test_coin):
    """Retrieve the latest metric for a given coin."""
    result = await db_session.execute(
        select(Metric)
        .where(Metric.coin_id == test_coin.id, Metric.is_active == True)
        .order_by(Metric.fetched_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()

    if not metric:
        return None  # No data found

    # ✅ Ensure we return a Pydantic model
    return MetricOut.model_validate(metric)
