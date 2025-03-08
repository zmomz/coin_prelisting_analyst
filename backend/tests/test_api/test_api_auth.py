import pytest
from httpx import AsyncClient  

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",  
        json={"email": "newuser@example.com", "password": "securepass", "name": "New User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, test_user):
    """Test user login with valid credentials."""
    response = await client.post(
        "/api/v1/auth/login",  
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"email": test_user.email, "password": "password"}  
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with incorrect password."""
    response = await client.post(
        "/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"}, 
        data={"email": "invalid@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
