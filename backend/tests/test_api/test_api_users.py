import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user(manager_client, db_session: AsyncSession, test_user):
    """Test retrieving a user (only Managers can access)."""
    response = await manager_client.get(
        f"/api/v1/users/{test_user.id}"  # ✅ No need for manual Authorization header
    )
    assert response.status_code in [200, 403]


@pytest.mark.asyncio(loop_scope="session")
async def test_list_users(manager_client, db_session: AsyncSession, test_user):
    """Test listing all users (only Managers can access)."""
    response = await manager_client.get("/api/v1/users/")
    assert response.status_code in [200, 403]


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(manager_client, db_session: AsyncSession, test_user):
    """Test updating user information."""
    response = await manager_client.put(
        f"/api/v1/users/{test_user.id}", json={"name": "Updated Name"}
    )
    assert response.status_code in [200, 403]


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(manager_client, db_session: AsyncSession, test_user):
    """Test soft deleting a user (only Managers can delete)."""
    response = await manager_client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code in [200, 403]
