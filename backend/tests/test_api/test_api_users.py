import pytest
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserOut
from app.core.config import settings

URL = f"{settings.API_V1_STR}/users/"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user(manager_client: AsyncClient, test_user):
    response = await manager_client.get(f"{URL}{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    parsed = UserOut.model_validate(data)
    assert parsed.id == test_user.id
    assert parsed.is_active is True


@pytest.mark.asyncio(loop_scope="session")
async def test_list_users(manager_client: AsyncClient):
    response = await manager_client.get(URL)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_list_users_pagination(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_not_found(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user(manager_client: AsyncClient, test_user):
    new_name = "Updated Name"
    response = await manager_client.put(
        f"{URL}{test_user.id}", json={"name": new_name}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_not_found(manager_client: AsyncClient):
    response = await manager_client.put(
        f"{URL}{uuid4()}", json={"name": "Ghost"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user(manager_client: AsyncClient, db_session: AsyncSession, test_user):
    response = await manager_client.delete(f"{URL}{test_user.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "User deleted successfully"

    await db_session.refresh(test_user)
    assert test_user.is_active is False


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_not_found(manager_client: AsyncClient):
    response = await manager_client.delete(f"{URL}{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


# 🔒 RBAC & Unauthorized Access


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_unauthorized(normal_client: AsyncClient, test_user):
    response = await normal_client.get(f"{URL}{test_user.id}")
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_unauthorized(normal_client: AsyncClient, test_user):
    response = await normal_client.put(
        f"{URL}{test_user.id}", json={"name": "Should Not Work"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_user_unauthorized(normal_client: AsyncClient, test_user):
    response = await normal_client.delete(f"{URL}{test_user.id}")
    assert response.status_code == 403


# 🧪 Schema contract validation


@pytest.mark.asyncio(loop_scope="session")
async def test_userout_schema_contract(manager_client: AsyncClient, test_user):
    response = await manager_client.get(f"{URL}{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    parsed = UserOut.model_validate(data)
    assert parsed.id == test_user.id
    assert parsed.is_active is True
