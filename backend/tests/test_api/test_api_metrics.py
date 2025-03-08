import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.metrics import create_metric
from app.schemas.metric import MetricCreate
import uuid


@pytest.mark.asyncio
async def test_get_metric(client: TestClient, db_session: AsyncSession):
    """Test retrieving a specific metric."""
    metric = await create_metric(
        db_session, 
        MetricCreate(coin_id=uuid.uuid4(), market_cap={"usd": 1000000}, volume_24h={"usd": 50000})
    )
    response = client.get(f"/api/v1/metrics/{metric.id}")
    assert response.status_code == 200
    assert response.json()["market_cap"]["usd"] == 1000000


@pytest.mark.asyncio
async def test_get_metrics_by_coin(client: TestClient, db_session: AsyncSession):
    """Test retrieving all metrics for a specific coin."""
    coin_id = uuid.uuid4()
    await create_metric(
        db_session, 
        MetricCreate(coin_id=coin_id, market_cap={"usd": 2000000}, volume_24h={"usd": 100000})
    )
    
    response = client.get(f"/api/v1/metrics/coin/{coin_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
