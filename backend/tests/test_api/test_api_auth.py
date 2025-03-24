import uuid

import pytest

from app.core.config import settings


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user(unauthorized_client):
    """Test user registration."""
    unique_email = f"newuser-{uuid.uuid4().hex[:8]}@example.com"
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": unique_email, "password": "securepass", "name": "New User"},
    )

    print("Register Response:", response.json())  # Debugging

    assert response.status_code == 201, response.text  # Ensure correct status code
    data = response.json()
    assert data["email"] == unique_email
    assert data["name"] == "New User"
    assert "id" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user(unauthorized_client):
    """Test user login using JSON."""
    unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpass"

    # Register user first
    register_response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": unique_email, "password": password, "name": "Test User"},
    )

    print("Register Response:", register_response.json())  # Debugging

    assert register_response.status_code == 201, register_response.text

    # Then login with JSON body
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "email": unique_email,
            "password": password,
        },  # Corrected to match new API
    )

    print("Login Response:", response.json())  # Debugging

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_invalid_credentials(unauthorized_client):
    """Test login with invalid credentials."""
    response = await unauthorized_client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpass",
        },  # ✅ Corrected format
    )

    print("Invalid Login Response:", response.json())  # Debugging

    assert response.status_code == 401, response.text  # Ensure it fails with 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Incorrect email or password"
