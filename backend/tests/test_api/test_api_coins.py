import logging
import uuid

import pytest
from httpx import AsyncClient

from app.core.config import settings

logger = logging.getLogger(__name__)

URL = f"{settings.API_V1_STR}/coins/"


def create_payload() -> dict:
    """Create a unique payload for creating a coin."""

    unique_symbol = f"TEST_{uuid.uuid4().hex[:6]}"
    unique_id = str(uuid.uuid4())
    request_payload = {
        "id": unique_id,
        "name": "Test Coin",
        "symbol": unique_symbol,
        "description": "A test coin",
        "github": "https://github.com/test/test",
        "coingeckoid": unique_symbol,
        "is_active": True,
    }
    return request_payload


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin(manager_client: AsyncClient):
    """Test creating a coin as a Manager."""

    request_payload = create_payload()
    response = await manager_client.post(url=URL, json=request_payload)

    assert (
        response.status_code == 201
    ), f"Expected 201 but got {response.status_code} with response {response.json()}"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_unauthorized(unauthorized_client: AsyncClient):
    """Test unauthorized user cannot create a coin."""

    request_payload = create_payload()
    response = await unauthorized_client.post(url=URL, json=request_payload)

    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_forbidden(normal_client: AsyncClient):
    """Test creating a coin without manager role."""

    request_payload = create_payload()
    response = await normal_client.post(url=URL, json=request_payload)

    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_coin(manager_client: AsyncClient, test_coin):
    """Test getting a coin by ID."""
    response = await manager_client.get(f"{URL}{test_coin.id}")  # ✅ Added `await`
    assert response.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_get_coin_not_found(manager_client: AsyncClient):
    """Test getting a non-existent coin."""
    response = await manager_client.get(  # ✅ Added `await`
        f"{settings.API_V1_STR}/coins/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Coin not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_coins(manager_client: AsyncClient, test_coins):
    """Test listing all coins."""
    response = await manager_client.get(
        f"{settings.API_V1_STR}/coins/"
    )  # ✅ Added `await`
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= len(test_coins)
    for coin in data:
        assert "id" in coin
        assert "name" in coin
        assert "symbol" in coin
        assert "description" in coin
        assert "github" in coin


@pytest.mark.asyncio(loop_scope="session")
async def test_update_coin(manager_client: AsyncClient, test_coin):
    """Test updating a coin while ensuring the symbol is unique."""

    # Generate a unique symbol
    unique_symbol = f"UPDT_{uuid.uuid4().hex[:6]}"  # e.g., UPDT_abc123

    response = await manager_client.put(
        f"{settings.API_V1_STR}/coins/{test_coin.id}",
        json={
            "name": "Updated Coin",
            "symbol": unique_symbol,  # ✅ Use a unique symbol to avoid conflicts
            "description": "An updated coin",
            "github": "https://github.com/test/updated",
        },
    )

    print("🔍 Update Coin Response:", response.status_code, response.json())

    assert (
        response.status_code == 200
    ), f"Expected 200 but got {response.status_code} with response {response.json()}"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_coin(manager_client: AsyncClient, test_coin):
    """Test deleting a coin."""
    response = await manager_client.delete(  # ✅ Added `await`
        f"{settings.API_V1_STR}/coins/{test_coin.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Coin deleted successfully"

    # Verify the coin is deleted
    response = await manager_client.get(  # ✅ Added `await`
        f"{settings.API_V1_STR}/coins/{test_coin.id}"
    )
    assert response.status_code == 404
