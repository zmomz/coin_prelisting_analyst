import uuid
import pytest
from httpx import AsyncClient
from app.schemas.metric import MetricOut
from app.core.config import settings
from datetime import datetime

URL = f"{settings.API_V1_STR}/metrics"


def create_metric_payload(coin_id: str) -> dict:
    return {
        "coin_id": coin_id,
        "market_cap": 1000000.0,
        "volume_24h": 50000.0,
        "liquidity": 250000.0,
        "github_activity": 120.0,
        "twitter_sentiment": 0.7,
        "reddit_sentiment": 0.9,
        "fetched_at": str(datetime.now())
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_metric(manager_client: AsyncClient, test_coin):
    payload = create_metric_payload(str(test_coin.id))
    response = await manager_client.post(f"{URL}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    parsed = MetricOut.model_validate(data)
    assert parsed.coin_id == test_coin.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_metric_unauthorized(normal_client, test_coin):
    payload = create_metric_payload(str(test_coin.id))
    response = await normal_client.post(f"{URL}/", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_create_metric_invalid(unauthorized_client, test_coin):
    payload = create_metric_payload(str(test_coin.id))
    payload.pop("market_cap")  # Remove required field
    response = await unauthorized_client.post(f"{URL}/", json=payload)
    assert response.status_code == 401  # unauthorized, not bad request


@pytest.mark.asyncio(loop_scope="session")
async def test_get_metric_by_id(manager_client, test_metrics):
    metric = test_metrics[0]
    response = await manager_client.get(f"{URL}/{metric.id}")
    assert response.status_code == 200
    parsed = MetricOut.model_validate(response.json())
    assert parsed.id == metric.id
    assert parsed.coin_id == metric.coin_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_metric_not_found(manager_client):
    response = await manager_client.get(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_list_metrics_by_coin(manager_client, test_coin, test_metrics):
    response = await manager_client.get(f"{URL}/coin/{test_coin.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_metrics)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_metric(manager_client, test_metrics):
    metric = test_metrics[0]
    update = {
        "github_activity": 222.0,
        "twitter_sentiment": 0.99
    }
    response = await manager_client.put(f"{URL}/{metric.id}", json=update)
    assert response.status_code == 200
    data = response.json()
    assert data["github_activity"] == 222.0
    assert data["twitter_sentiment"] == 0.99


@pytest.mark.asyncio(loop_scope="session")
async def test_update_metric_unauthorized(normal_client, test_metrics):
    metric = test_metrics[0]
    response = await normal_client.put(f"{URL}/{metric.id}", json={"github_activity": 111.0})
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_update_metric_not_found(manager_client):
    response = await manager_client.put(f"{URL}/{uuid.uuid4()}", json={"github_activity": 111.0})
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_metric(manager_client, test_metrics):
    metric = test_metrics[0]
    response = await manager_client.delete(f"{URL}/{metric.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Metric deleted successfully"

    # Ensure it's soft-deleted
    response = await manager_client.get(f"{URL}/{metric.id}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_metric_unauthorized(normal_client, test_metrics):
    metric = test_metrics[0]
    response = await normal_client.delete(f"{URL}/{metric.id}")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_metric_not_found(manager_client):
    response = await manager_client.delete(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404
