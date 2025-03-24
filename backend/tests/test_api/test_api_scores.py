import uuid

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.schemas.score import ScoreOut

URL = f"{settings.API_V1_STR}/scores"


def build_score_payload(coin_id, scoring_weight_id):
    return {
        "coin_id": str(coin_id),
        "scoring_weight_id": str(scoring_weight_id),
        "liquidity_score": 0.6,
        "developer_score": 0.7,
        "community_score": 0.8,
        "market_score": 0.9,
        "final_score": 0.75,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_score(manager_client: AsyncClient, test_coin, scoring_weight):
    payload = build_score_payload(test_coin.id, scoring_weight.id)
    response = await manager_client.post(f"{URL}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["coin_id"] == str(test_coin.id)
    assert data["scoring_weight_id"] == str(scoring_weight.id)
    assert 0.0 <= data["final_score"] <= 1.0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_score(manager_client: AsyncClient, test_coin, scoring_weight):
    payload = build_score_payload(test_coin.id, scoring_weight.id)
    create_resp = await manager_client.post(f"{URL}/", json=payload)
    score_id = create_resp.json()["id"]

    response = await manager_client.get(f"{URL}/{score_id}")
    assert response.status_code == 200
    ScoreOut.model_validate(response.json())


@pytest.mark.asyncio(loop_scope="session")
async def test_get_score_not_found(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_get_scores_by_coin(manager_client: AsyncClient, test_coin, scoring_weight):
    # Ensure at least one exists
    await manager_client.post(f"{URL}/", json=build_score_payload(test_coin.id, scoring_weight.id))

    response = await manager_client.get(f"{URL}/by-coin/{test_coin.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("final_score" in score for score in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_score(manager_client: AsyncClient, test_coin, scoring_weight):
    create_resp = await manager_client.post(
        f"{URL}/", json=build_score_payload(test_coin.id, scoring_weight.id)
    )
    score_id = create_resp.json()["id"]

    update_resp = await manager_client.put(
        f"{URL}/{score_id}",
        json={
            "liquidity_score": 0.1,
            "developer_score": 0.2,
            "community_score": 0.3,
            "market_score": 0.4,
            "final_score": 0.25,
        },
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["liquidity_score"] == 0.1
    assert data["final_score"] == 0.25


@pytest.mark.asyncio(loop_scope="session")
async def test_update_score_not_found(manager_client: AsyncClient):
    response = await manager_client.put(
        f"{URL}/{uuid.uuid4()}",
        json={
            "liquidity_score": 0.5,
            "developer_score": 0.5,
            "community_score": 0.5,
            "market_score": 0.5,
            "final_score": 0.5,
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_score(manager_client: AsyncClient, test_coin, scoring_weight):
    create_resp = await manager_client.post(
        f"{URL}/", json=build_score_payload(test_coin.id, scoring_weight.id)
    )
    score_id = create_resp.json()["id"]

    delete_resp = await manager_client.delete(f"{URL}/{score_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["detail"] == "Score deleted successfully"

    # Confirm it's gone
    resp = await manager_client.get(f"{URL}/{score_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_score_not_found(manager_client: AsyncClient):
    response = await manager_client.delete(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_score_permissions(normal_client: AsyncClient, test_coin, scoring_weight):
    payload = build_score_payload(test_coin.id, scoring_weight.id)

    # Non-manager create
    r1 = await normal_client.post(f"{URL}/", json=payload)
    assert r1.status_code == 403

    # Non-manager delete
    r2 = await normal_client.delete(f"{URL}/{uuid.uuid4()}")
    assert r2.status_code == 403

    # Non-manager update
    r3 = await normal_client.put(f"{URL}/{uuid.uuid4()}", json=payload)
    assert r3.status_code == 403
