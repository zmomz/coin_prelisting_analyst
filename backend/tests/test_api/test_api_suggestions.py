import uuid
import pytest
from httpx import AsyncClient

from app.core.security import get_password_hash
from app.models.suggestion import Suggestion, SuggestionStatus
from app.core.config import settings
from app.models.user import User, UserRole

URL = f"{settings.API_V1_STR}/suggestions"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_suggestion(
        normal_client: AsyncClient, test_coin, test_user
        ):
    payload = {
        "coin_id": str(test_coin.id),
        "note": "Looks promising",
    }
    response = await normal_client.post(f"{URL}/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["note"] == "Looks promising"
    assert data["coin_id"] == str(test_coin.id)
    assert data["user_id"] == str(test_user.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_create_suggestion_unauthenticated(
        unauthorized_client: AsyncClient, test_coin
        ):
    payload = {"coin_id": str(test_coin.id), "note": "Should fail"}
    response = await unauthorized_client.post(f"{URL}/", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_get_suggestion_by_id(
        manager_client: AsyncClient, test_suggestion_pending
        ):
    response = await manager_client.get(f"{URL}/{test_suggestion_pending.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(test_suggestion_pending.id)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_suggestions_by_coin(
        manager_client: AsyncClient,
        test_coin, test_suggestion_pending
        ):
    response = await manager_client.get(f"{URL}/coin/{test_coin.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["id"] == str(test_suggestion_pending.id) for s in data)


@pytest.mark.asyncio(loop_scope="session")
async def test_update_suggestion_note_by_user(normal_client: AsyncClient, test_suggestion_pending):
    payload = {"note": "Updated note"}
    response = await normal_client.put(f"{URL}/{test_suggestion_pending.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["note"] == "Updated note"


@pytest.mark.asyncio(loop_scope="session")
async def test_update_suggestion_note_and_status_by_manager(manager_client: AsyncClient, test_suggestion_pending):
    payload = {"note": "Manager updated", "status": SuggestionStatus.APPROVED.value}
    response = await manager_client.put(f"{URL}/{test_suggestion_pending.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["note"] == "Manager updated"
    assert data["status"] == SuggestionStatus.APPROVED.value


@pytest.mark.asyncio(loop_scope="session")
async def test_update_other_user_suggestion_forbidden(normal_client: AsyncClient, db_session, test_coin):
    # 👤 Create a second user (not the one tied to `normal_client`)
    other_user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        hashed_password=get_password_hash("otherpass"),
        name="Other User",
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    # 💬 Create suggestion by the other user
    suggestion = Suggestion(
        id=uuid.uuid4(),
        coin_id=test_coin.id,
        user_id=other_user.id,
        note="Other's suggestion",
        status=SuggestionStatus.APPROVED,
        is_active=True,
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)

    # 🛡 Attempt to update as the original user (normal_client)
    payload = {"note": "Should not work"}
    response = await normal_client.put(f"{URL}/{suggestion.id}", json=payload)

    assert response.status_code == 403



@pytest.mark.asyncio(loop_scope="session")
async def test_delete_suggestion_by_owner(normal_client: AsyncClient, test_suggestion_pending):
    response = await normal_client.delete(f"{URL}/{test_suggestion_pending.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Suggestion deleted successfully"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_suggestion_by_manager(manager_client: AsyncClient, test_suggestion_approved):
    response = await manager_client.delete(f"{URL}/{test_suggestion_approved.id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Suggestion deleted successfully"


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_suggestion_unauthorized(normal_client: AsyncClient):
    random_id = uuid.uuid4()
    response = await normal_client.delete(f"{URL}/{random_id}")
    assert response.status_code in [403, 404]


@pytest.mark.asyncio(loop_scope="session")
async def test_update_suggestion_not_found(manager_client: AsyncClient):
    payload = {"note": "Nothing"}
    response = await manager_client.put(f"{URL}/{uuid.uuid4()}", json=payload)
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_get_suggestion_not_found(manager_client: AsyncClient):
    response = await manager_client.get(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_suggestion_not_found(manager_client: AsyncClient):
    response = await manager_client.delete(f"{URL}/{uuid.uuid4()}")
    assert response.status_code == 404
