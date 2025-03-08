import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # In-memory SQLite for testing

engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """Fixture to set up the test database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session():
    """Fixture to provide a database session for testing."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture()
def client():
    """Fixture to provide a FastAPI test client."""
    return TestClient(app)


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
    return user
