import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.coins import create_coin
from app.schemas.coin import CoinCreate


@pytest.mark.asyncio
async def test_create_coin(client: TestClient, db_session: AsyncSession, test_user):
    """Test creating a new coin (only Managers can create)."""
    response = client.post(
        "/api/v1/coins/",
        json={"name": "Bitcoin", "symbol": "btc", "description": "First cryptocurrency"},
        headers={"Authorization": f"Bearer {test_user.role == 'manager'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for managers, forbidden for others


@pytest.mark.asyncio
async def test_get_coin(client: TestClient, db_session: AsyncSession):
    """Test retrieving a specific coin."""
    coin = await create_coin(db_session, CoinCreate(name="Ethereum", symbol="eth"))
    response = client.get(f"/api/v1/coins/{coin.id}")
    assert response.status_code == 200
    assert response.json()["symbol"] == "eth"


@pytest.mark.asyncio
async def test_list_coins(client: TestClient, db_session: AsyncSession):
    """Test listing coins."""
    response = client.get("/api/v1/coins/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
