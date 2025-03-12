import pytest
import logging
from httpx import AsyncClient
from app.core.config import settings
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.coin import Coin
from sqlalchemy import delete

logger = logging.getLogger(__name__)  # ✅ Initialize logger



@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin(manager_client: AsyncClient):
    """Test creating a coin as a Manager."""
    unique_symbol = f"TEST_{uuid.uuid4().hex[:6]}"  # Unique symbol for each test
    unique_id = str(uuid.uuid4())
    request_payload = {
        "id": unique_id,
        "name": "Test Coin",
        "symbol": unique_symbol,
        "description": "A test coin",
        "github": "https://github.com/test/test"
    }

    response = await manager_client.post(
        f"{settings.API_V1_STR}/coins/",
        json=request_payload
    )

    print("🔍 Response Status:", response.status_code)
    print("🔍 Response Body:", response.json())  # Print the API response for debugging

    assert response.status_code == 201, f"Expected 201 but got {response.status_code} with response {response.json()}"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_unauthorized(unauthorized_client: AsyncClient, db_session: AsyncSession):
    """Test unauthorized user cannot create a coin."""

    # 🧹 Cleanup: Ensure no existing coin with symbol "TEST" before running the test
    existing_coin = await db_session.execute(select(Coin).filter_by(symbol="TEST"))
    if existing_coin.scalar():
        await db_session.execute(delete(Coin).where(Coin.symbol == "TEST"))
        await db_session.commit()

# 🕵️‍♂️ Debug: Print client headers to check authentication
    print("🔍 Request Headers:", unauthorized_client.headers)
    # 🚀 Make the unauthorized request (without authentication)
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/coins/",
        json={
            "name": "Test Coin",
            "symbol": "TEST",
            "description": "A test coin",
            "github": "https://github.com/test/test"
        }
    )

    # 🛠 Debugging: Print the response if the test fails
    if response.status_code != 401:
        print(f"❌ Unexpected Status: {response.status_code}")
        print(f"❌ Response Body: {response.text}")
    if response.status_code == 401:
        print("🟢 Test passed: Expected 401 Unauthorized")
        print(f"❌ Unexpected Status: {response.status_code}")
        print(f"❌ Response Body: {response.text}")

    # ✅ Assert expected response
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"



@pytest.mark.asyncio(loop_scope="session")
async def test_create_coin_forbidden(authenticated_client: AsyncClient):
    """Test creating a coin without manager role."""
    response = await authenticated_client.post(  # ✅ Added `await`
        f"{settings.API_V1_STR}/coins/",
        json={
            "name": "Test Coin",
            "symbol": "TEST",
            "description": "A test coin",
            "github": "https://github.com/test/test"
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Not enough permissions"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_coin(manager_client: AsyncClient, test_coin):
    """Test getting a coin by ID."""
    response = await manager_client.get(  # ✅ Added `await`
        f"{settings.API_V1_STR}/coins/{test_coin.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_coin.id)
    assert data["name"] == test_coin.name
    assert data["symbol"] == test_coin.symbol
    assert data["description"] == test_coin.description
    assert data["github"] == test_coin.github


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
    response = await manager_client.get(f"{settings.API_V1_STR}/coins/")  # ✅ Added `await`
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
            "github": "https://github.com/test/updated"
        }
    )

    print("🔍 Update Coin Response:", response.status_code, response.json())

    assert response.status_code == 200, f"Expected 200 but got {response.status_code} with response {response.json()}"



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
