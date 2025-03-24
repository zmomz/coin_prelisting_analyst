import uuid

import pytest
from httpx import AsyncClient

from app.core.config import settings

URL = f"{settings.API_V1_STR}/scoring-weights/"


def get_unique_weight_payload() -> dict:
    return {
        "liquidity_score": 0.3,
        "developer_score": 0.2,
        "community_score": 0.2,
        "market_score": 0.3,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_scoring_weight(manager_client: AsyncClient):
    payload = get_unique_weight_payload()
    response = await manager_client.post(URL, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert all(k in data for k in payload)
    assert data["liquidity_score"] == payload["liquidity_score"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_scoring_weight_unauthorized(normal_client: AsyncClient):
    payload = get_unique_weight_payload()
    response = await normal_client.post(URL, json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_get_scoring_weight(manager_client: AsyncClient, scoring_weight):
    response = await manager_client.get(f"{URL}{scoring_weight.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(scoring_weight.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_scoring_weight_not_found(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_list_scoring_weights(manager_client: AsyncClient, scoring_weight):
    response = await manager_client.get(URL)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(w["id"] == str(scoring_weight.id) for w in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_scoring_weight(manager_client: AsyncClient, scoring_weight):
    response = await manager_client.put(
        f"{URL}{scoring_weight.id}",
        json={
            "liquidity_score": 0.25,
            "developer_score": 0.25,
            "community_score": 0.25,
            "market_score": 0.25,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["liquidity_score"] == 0.25


@pytest.mark.asyncio(loop_scope="session")
async def test_update_scoring_weight_not_found(manager_client: AsyncClient):
    response = await manager_client.put(
        f"{URL}{uuid.uuid4()}",
        json=get_unique_weight_payload(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_scoring_weight(manager_client: AsyncClient, scoring_weight):
    response = await manager_client.delete(f"{URL}{scoring_weight.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Scoring weight deleted successfully"

    # Check it's actually gone
    response = await manager_client.get(f"{URL}{scoring_weight.id}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_scoring_weight_not_found(manager_client: AsyncClient):
    response = await manager_client.delete(f"{URL}{uuid.uuid4()}")
    assert response.status_code == 404
