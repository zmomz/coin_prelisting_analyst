import uuid

import pytest

from app.core.config import settings
from app.schemas.auth import Token
from app.schemas.user import UserOut


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user(unauthorized_client):
    """Test successful user registration."""
    unique_email = f"newuser-{uuid.uuid4().hex[:8]}@example.com"
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": unique_email, "password": "securepass", "name": "New User"},
    )

    assert response.status_code == 201
    data = response.json()
    parsed = UserOut.model_validate(data)

    assert parsed.email == unique_email
    assert parsed.name == "New User"
    assert parsed.is_active is True
    assert parsed.role.value == "analyst"


@pytest.mark.asyncio(loop_scope="session")
async def test_register_existing_user(unauthorized_client):
    """Registering with an existing email should fail."""
    email = f"dupeuser-{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "pass", "name": "Dup"}

    # First time should work
    first = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register", json=payload
    )
    assert first.status_code == 201

    # Second time should fail
    second = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register", json=payload
    )
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user_success(unauthorized_client):
    """Register and login a user with correct credentials."""
    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    password = "mypassword"

    # Register first
    await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password, "name": "Test Login"},
    )

    # Login
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 200
    data = response.json()
    parsed = Token.model_validate(data)

    assert parsed.token_type == "bearer"
    assert isinstance(parsed.access_token, str)
    assert len(parsed.access_token) > 10


@pytest.mark.asyncio(loop_scope="session")
async def test_login_wrong_password(unauthorized_client):
    """Login with wrong password should fail."""
    email = f"wrongpw-{uuid.uuid4().hex[:8]}@example.com"
    password = "correctpass"

    await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "password": password},
    )

    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "WRONG"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_nonexistent_user(unauthorized_client):
    """Login with a user that doesn't exist should fail."""
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "ghost@example.com", "password": "nopass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
