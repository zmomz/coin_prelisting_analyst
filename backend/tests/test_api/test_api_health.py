import pytest
from httpx import AsyncClient
from app.main import app
from app.db.session import get_db
from tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_healthcheck_success(client: AsyncClient):
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    app.dependency_overrides = {}



@pytest.mark.asyncio
async def test_healthcheck_db_failure(client: AsyncClient):
    class DummySession:
        async def execute(self, *_):
            raise Exception("DB down")

        async def close(self):
            pass

    async def override_broken_db():
        yield DummySession()

    app.dependency_overrides[get_db] = override_broken_db

    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "Database connection failed" in response.json()["message"]

    app.dependency_overrides = {}
