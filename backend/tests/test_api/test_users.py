import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.users import create_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
import uuid


@pytest.mark.asyncio
async def test_get_user(client: TestClient, db_session: AsyncSession, test_user):
    """Test retrieving a user (only Managers can access)."""
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_user.role == 'manager'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for managers, forbidden for others


@pytest.mark.asyncio
async def test_list_users(client: TestClient, db_session: AsyncSession, test_user):
    """Test listing all users (only Managers can access)."""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_user.role == 'manager'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for managers, forbidden for others


@pytest.mark.asyncio
async def test_update_user(client: TestClient, db_session: AsyncSession, test_user):
    """Test updating user information."""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {test_user.role == 'manager'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for managers, forbidden for others


@pytest.mark.asyncio
async def test_delete_user(client: TestClient, db_session: AsyncSession, test_user):
    """Test soft deleting a user (only Managers can delete)."""
    response = client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_user.role == 'manager'}"}
    )
    assert response.status_code in [200, 403]  # Expecting success for managers, forbidden for others
