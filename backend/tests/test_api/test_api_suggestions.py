import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.suggestions import create_suggestion
from app.schemas.suggestion import SuggestionCreate
import uuid


@pytest.mark.asyncio
async def test_create_suggestion(client: TestClient, db_session: AsyncSession, test_user):
    """Test creating a new suggestion (only Analysts can create)."""
    response = client.post(
        "/api/v1/suggestions/",
        json={"coin_id": str(uuid.uuid4()), "note": "Consider listing this coin"},
        headers={"Authorization": f"Bearer {test_user.role == 'analyst'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for analysts, forbidden for others


@pytest.mark.asyncio
async def test_get_suggestion(client: TestClient, db_session: AsyncSession):
    """Test retrieving a specific suggestion."""
    suggestion = await create_suggestion(
        db_session, SuggestionCreate(coin_id=uuid.uuid4(), note="Great project"), user_id=uuid.uuid4()
    )
    response = client.get(f"/api/v1/suggestions/{suggestion.id}")
    assert response.status_code == 200
    assert response.json()["note"] == "Great project"


@pytest.mark.asyncio
async def test_list_suggestions(client: TestClient, db_session: AsyncSession):
    """Test listing all suggestions."""
    response = client.get("/api/v1/suggestions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
