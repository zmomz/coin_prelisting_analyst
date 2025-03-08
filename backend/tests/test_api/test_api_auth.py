import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepass", "name": "New User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_login_user(client: TestClient, test_user):
    """Test user login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "password"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "invalid@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
