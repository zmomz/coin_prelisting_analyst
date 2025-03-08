import pytest
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.main import app
from httpx import AsyncClient
import asyncio
from fastapi.testclient import TestClient

# Use the test database URL
DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# Create an async database engine
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """Fixture to set up the test database before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Tests run here
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def db_session():
    """Fixture to provide an async database session for testing."""
    async with TestingSessionLocal() as session:
        yield session  # Provide session to test functions

@pytest.fixture(autouse=True)
async def override_get_db(db_session):
    """Override the get_db dependency to use the test session correctly."""
    async def _get_db():
        async with db_session() as session:
            yield session  # Ensure session is actually used
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def event_loop():
    """Ensure a single event loop for the entire test session."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
async def client():
    """Fixture to provide an async HTTP client for FastAPI testing."""
    test_client = TestClient(app)  # Start FastAPI test server
    async with AsyncClient(base_url="http://localhost", transport=test_client.transport) as client:
        yield client

@pytest.fixture()
async def test_user(db_session):
    """Fixture to create a test user."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        name="Test User",
        role=UserRole.ANALYST,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user  # Ensure fixture returns the user object, not a coroutine

@pytest.fixture()
def celery_config():
    """Configure Celery to run tasks eagerly during tests."""
    return {
        "task_always_eager": True,  # Ensures tasks execute immediately in test mode
    }
