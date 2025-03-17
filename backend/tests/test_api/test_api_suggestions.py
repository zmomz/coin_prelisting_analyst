import pytest
import uuid
from httpx import AsyncClient
from app.models.suggestion import SuggestionStatus
from app.core.config import settings


@pytest.mark.asyncio(loop_scope="session")
async def test_create_suggestion(authenticated_client: AsyncClient, test_coin):
    """Test creating a new suggestion."""
    response = await authenticated_client.post(
        f"{settings.API_V1_STR}/suggestions/",
        json={
            "coin_id": str(test_coin.id),
            "note": "This is a test suggestion",  # 🔹 Changed from "title" to "note"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["coin_id"] == str(test_coin.id)
    assert data["note"] == "This is a test suggestion"  # 🔹 Updated check


@pytest.mark.asyncio(loop_scope="session")
async def test_get_suggestion(authenticated_client: AsyncClient, test_suggestion_approved):
    """Test retrieving a suggestion by ID."""
    response = await authenticated_client.get(
        f"{settings.API_V1_STR}/suggestions/{test_suggestion_approved.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_suggestion_approved.id)
    assert data["coin_id"] == str(test_suggestion_approved.coin_id)
    assert data["note"] == test_suggestion_approved.note  # 🔹 Updated check


@pytest.mark.asyncio(loop_scope="session")
async def test_get_suggestions(authenticated_client: AsyncClient, test_suggestion_approved):
    """Test listing all suggestions."""
    response = await authenticated_client.get(f"{settings.API_V1_STR}/suggestions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["id"] == str(test_suggestion_approved.id) for s in data)  # 🔹 Fixed list check


@pytest.mark.asyncio(loop_scope="session")
async def test_update_suggestion(authenticated_client: AsyncClient, test_suggestion_approved):
    """Test updating a suggestion."""
    response = await authenticated_client.put(
        f"{settings.API_V1_STR}/suggestions/{test_suggestion_approved.id}",
        json={
            "note": "Updated test suggestion",  # 🔹 Changed from "title" to "note"
            "status": "approved"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["note"] == "Updated test suggestion"  # 🔹 Updated check
    assert data["status"] == SuggestionStatus.APPROVED.value


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_suggestion(manager_client: AsyncClient, test_suggestion_approved):
    """Test deleting a suggestion."""
    response = await manager_client.delete(
        f"{settings.API_V1_STR}/suggestions/{test_suggestion_approved.id}"
    )
    assert response.status_code == 200  # 🔹 Check for successful deletion
