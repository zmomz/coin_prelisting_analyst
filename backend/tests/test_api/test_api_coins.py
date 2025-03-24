import uuid
import pytest
import logging
from httpx import AsyncClient
from app.core.config import settings

logger = logging.getLogger(__name__)
URL = f"{settings.API_V1_STR}/coins/"


def create_payload() -> dict:
    unique_symbol = f"TEST_{uuid.uuid4().hex[:6]}"
    return {
        "id": str(uuid.uuid4()),
        "name": "Test Coin",
        "symbol": unique_symbol,
        "description": "A test coin",
        "github": "https://github.com/test/test",
        "coingeckoid": unique_symbol,
        "is_active": True,
    }


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin(manager_client: AsyncClient):
    payload = create_payload()
    response = await manager_client.post(URL, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == payload["symbol"]
    assert data["description"] == payload["description"]


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_unauthorized(unauthorized_client: AsyncClient):
    payload = create_payload()
    response = await unauthorized_client.post(URL, json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_forbidden(normal_client: AsyncClient):
    payload = create_payload()
    response = await normal_client.post(URL, json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_duplicate_symbol(manager_client: AsyncClient):
    payload = create_payload()
    await manager_client.post(URL, json=payload)

    duplicate_payload = payload.copy()
    duplicate_payload["id"] = str(uuid.uuid4())  # New ID, same symbol
    response = await manager_client.post(URL, json=duplicate_payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Coin symbol already exists"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_invalid_payload(manager_client: AsyncClient):
    invalid_payload = {"name": "Missing required fields"}
    response = await manager_client.post(URL, json=invalid_payload)
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_get_coin(manager_client: AsyncClient, test_coin):
    response = await manager_client.get(f"{URL}{test_coin.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_coin.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_coin_not_found(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Coin not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_coins(manager_client: AsyncClient, test_coins):
    response = await manager_client.get(URL)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_coins)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_coin(manager_client: AsyncClient, test_coin):
    unique_symbol = f"UPD_{uuid.uuid4().hex[:6]}"
    update_data = {
        "name": "Updated Coin",
        "symbol": unique_symbol,
        "description": "Updated description",
        "github": "https://github.com/test/updated",
    }

    response = await manager_client.put(f"{URL}{test_coin.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == unique_symbol
    assert data["description"] == "Updated description"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_coin_not_found(manager_client: AsyncClient):
    update_data = {"name": "Should fail"}
    response = await manager_client.put(
        f"{URL}00000000-0000-0000-0000-000000000000", json=update_data
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Coin not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_coin(manager_client: AsyncClient, test_coin):
    response = await manager_client.delete(f"{URL}{test_coin.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Coin deleted successfully"

    # Check that it's soft-deleted
    response = await manager_client.get(f"{URL}{test_coin.id}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_coin_not_found(manager_client: AsyncClient):
    response = await manager_client.delete(f"{URL}00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["detail"] == "Coin not found"
