import pytest
from httpx import AsyncClient
from sqlalchemy.future import select

from app.core.config import settings
from app.models.metric import Metric


@pytest.mark.asyncio(loop_scope="session")
async def test_get_metric(authenticated_client: AsyncClient, test_metrics, db_session):
    """Test retrieving a single metric."""

    # Fetch all metrics from DB
    result = await db_session.execute(select(Metric))
    all_metrics = result.scalars().all()
    print("\n🚀 All metrics in DB before API call:", all_metrics)

    # Ensure we have at least one metric to test
    assert len(test_metrics) > 0, "❌ No test metrics available!"

    # Select first metric
    metric = test_metrics[0]

    # Debug prints for ID verification
    print(f"🆔 Metric ID for API Call: {metric.id} (Type: {type(metric.id)})")

    # Verify if this metric exists in DB
    db_result = await db_session.execute(select(Metric).where(Metric.id == metric.id))
    db_metric = db_result.scalar_one_or_none()
    print("✅ Metric found in DB:", db_metric)

    # Ensure metric exists in DB
    assert db_metric is not None, f"❌ Metric ID {metric.id} not found in DB!"

    # Perform API request
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/metrics/{metric.id}"
    )

    print("📢 API Response Status Code:", response.status_code)
    print("📢 API Response JSON:", response.json())

    # Validate response
    assert response.status_code == 200, f"❌ Expected 200, got {response.status_code}"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_metrics_by_coin(
    authenticated_client: AsyncClient, test_coin, test_metrics, db_session
):
    """Test retrieving all metrics for a specific coin."""

    # Debug prints for Coin ID
    print(f"\n🆔 Coin ID for API Call: {test_coin.id} (Type: {type(test_coin.id)})")

    # Verify if this coin exists in DB
    db_result = await db_session.execute(
        select(Metric).where(Metric.coin_id == test_coin.id)
    )
    db_metrics = db_result.scalars().all()
    print("✅ Metrics found in DB for Coin:", db_metrics)

    # Ensure the coin has metrics
    assert len(db_metrics) > 0, f"❌ No metrics found for Coin ID {test_coin.id}!"

    # Perform API request
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/metrics/coin/{test_coin.id}"
    )

    print("📢 API Response Status Code:", response.status_code)
    print("📢 API Response JSON:", response.json())

    # Validate response
    assert response.status_code == 200, f"❌ Expected 200, got {response.status_code}"

    data = response.json()
    assert len(data) == len(
        test_metrics
    ), f"❌ Mismatch: Expected {len(test_metrics)}, got {len(data)}"

    for i, metric in enumerate(test_metrics):
        assert data[i]["id"] == str(metric.id), f"❌ Mismatch in metric ID at index {i}"
        assert data[i]["coin_id"] == str(
            metric.coin_id
        ), f"❌ Mismatch in coin ID at index {i}"
        assert (
            data[i]["market_cap"]["value"] == metric.market_cap["value"]
        ), f"❌ Market Cap mismatch at index {i}"
        assert (
            data[i]["market_cap"]["currency"] == "USD"
        ), f"❌ Currency mismatch at index {i}"
