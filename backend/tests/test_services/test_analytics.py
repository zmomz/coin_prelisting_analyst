import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics import get_latest_metrics
from app.crud.metrics import create_metric
from app.schemas.metric import MetricCreate
import uuid


@pytest.mark.asyncio
async def test_get_latest_metrics(db_session: AsyncSession):
    """Test retrieving the latest metrics for a specific coin."""
    coin_id = uuid.uuid4()

    # Create two metric records with different timestamps
    await create_metric(
        db_session, 
        MetricCreate(coin_id=coin_id, market_cap={"usd": 1000000}, volume_24h={"usd": 50000})
    )
    
    await create_metric(
        db_session, 
        MetricCreate(coin_id=coin_id, market_cap={"usd": 2000000}, volume_24h={"usd": 100000})
    )

    latest_metrics = await get_latest_metrics(db_session, coin_id)
    assert latest_metrics is not None
    assert latest_metrics["market_cap"]["usd"] == 2000000
    assert latest_metrics["volume_24h"]["usd"] == 100000
