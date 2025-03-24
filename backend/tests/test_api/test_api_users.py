import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserOut


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user(manager_client, test_user):
    response = await manager_client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["is_active"] is True
    assert "email" in data and "role" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_list_users(manager_client):
    response = await manager_client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(manager_client, test_user):
    new_name = "Updated Name"
    response = await manager_client.put(
        f"/api/v1/users/{test_user.id}", json={"name": new_name}
    )
    assert response.status_code == 200
    assert response.json()["name"] == new_name


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(manager_client, db_session: AsyncSession, test_user):
    response = await manager_client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"

    await db_session.refresh(test_user)
    assert test_user.is_active is False


# ✅ Edge case and RBAC tests below


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_unauthorized(normal_client, test_user):
    response = await normal_client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_not_found(manager_client):
    response = await manager_client.get(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_unauthorized(normal_client, test_user):
    response = await normal_client.put(
        f"/api/v1/users/{test_user.id}", json={"name": "Should Not Work"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_not_found(manager_client):
    response = await manager_client.put(
        f"/api/v1/users/{uuid4()}", json={"name": "Ghost"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_unauthorized(normal_client, test_user):
    response = await normal_client.delete(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_not_found(manager_client):
    response = await manager_client.delete(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_list_users_pagination(manager_client):
    response = await manager_client.get("/api/v1/users/?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_userout_schema_contract(manager_client, test_user):
    response = await manager_client.get(f"/api/v1/users/{test_user.id}")
    data = response.json()
    parsed = UserOut.model_validate(data)
    assert parsed.id == test_user.id
    assert parsed.is_active is True
