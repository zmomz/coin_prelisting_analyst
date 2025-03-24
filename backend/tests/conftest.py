"""Test setup for async FastAPI app with database and fixtures."""

import uuid

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    Coin, Metric, ScoringWeight, User, UserRole, Suggestion, SuggestionStatus
)

TEST_PASSWORD = "testpass"


# 🔧 Logging
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    configure_logging()


# 🔧 DB setup
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Create & drop all tables once per session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Fresh session per test function."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(db_session: AsyncSession):
    """Truncate all tables before each test."""
    tables = [
        "coins", "metrics", "scores", "scoring_weights",
        "suggestions", "user_activities", "users"
    ]
    for table in tables:
        await db_session.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
    await db_session.commit()


# 🔧 Dependency override
@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_get_db():
    async def _get_test_db():
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


# 🔧 Clients
@pytest_asyncio.fixture(scope="session")
async def client(init_test_db, override_get_db):
    """Main client with app lifespan."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            response = await ac.get("/api/health")
            assert response.status_code == 200
            yield ac


@pytest_asyncio.fixture(scope="function")
async def unauthorized_client(client: AsyncClient):
    """Client with no Authorization header."""
    original_headers = client.headers.copy()
    client.headers.pop("Authorization", None)
    yield client
    client.headers = original_headers


@pytest_asyncio.fixture(scope="function")
async def normal_client(client: AsyncClient, test_user: User):
    """Client authenticated as a normal user."""
    original_headers = client.headers.copy()
    token = create_access_token({"sub": str(test_user.id)})
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    client.headers = original_headers


@pytest_asyncio.fixture(scope="function")
async def manager_client(client: AsyncClient, db_session: AsyncSession):
    """Client authenticated as a manager."""
    original_headers = client.headers.copy()

    await db_session.execute(delete(User))
    await db_session.commit()

    email = f"manager_{uuid.uuid4().hex[:6]}@example.com"

    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": TEST_PASSWORD,
        "name": "Test Manager",
        "role": "manager",
    })

    login = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": TEST_PASSWORD,
    })

    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    client.headers = original_headers



# 🧪 Fixtures
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password=get_password_hash(TEST_PASSWORD),
        name="Test User",
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_coin(db_session):
    symbol = f"TST_{uuid.uuid4().hex[:4]}"
    coin = Coin(
        id=uuid.uuid4(),
        coingeckoid=symbol,
        name=symbol,
        symbol=symbol,
        description="Test Coin",
        github="https://github.com/testcoin",
        is_active=True,
        created_at=func.now(),
    )
    db_session.add(coin)
    await db_session.commit()
    await db_session.refresh(coin)
    return coin


@pytest_asyncio.fixture(scope="function")
async def test_coins(db_session):
    coin_data = [
        {"id": "btc", "symbol": "BTC", "name": "Bitcoin", "github": "https://github.com/bitcoin"},
        {"id": "eth", "symbol": "ETH", "name": "Ethereum", "github": "https://github.com/ethereum"},
        {"id": "sol", "symbol": "SOL", "name": "Solana", "github": "https://github.com/solana"},
    ]
    coins = []
    for c in coin_data:
        coin = Coin(
            id=uuid.uuid4(),
            coingeckoid=c["id"],
            name=c["name"],
            symbol=c["symbol"],
            github=c["github"],
            is_active=True,
            created_at=func.now(),
        )
        db_session.add(coin)
        coins.append(coin)
    await db_session.commit()
    for coin in coins:
        await db_session.refresh(coin)
    return coins


@pytest_asyncio.fixture(scope="function")
async def test_metrics(db_session, test_coin):
    metrics = []
    for _ in range(3):
        m = Metric(
            id=uuid.uuid4(),
            coin_id=test_coin.id,
            market_cap={"value": 1_000_000},
            volume_24h={"value": 50_000},
            liquidity={"value": 100_000},
            github_activity={"count": 10},
            twitter_sentiment={"score": 0.8},
            reddit_sentiment={"score": 0.9},
            fetched_at=func.now(),
            is_active=True,
            created_at=func.now(),
        )
        db_session.add(m)
        metrics.append(m)
    await db_session.commit()
    for m in metrics:
        await db_session.refresh(m)
    return metrics


@pytest_asyncio.fixture(scope="function")
async def scoring_weight(db_session):
    w = ScoringWeight(
        liquidity_score=0.3,
        developer_score=0.2,
        community_score=0.2,
        market_score=0.3,
        created_at=func.now(),
    )
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)
    return w


@pytest_asyncio.fixture(scope="function")
async def test_suggestion_pending(db_session: AsyncSession, test_coin, test_user):
    """Fixture for a pending suggestion owned by test_user."""
    suggestion = Suggestion(
        id=uuid.uuid4(),
        coin_id=test_coin.id,
        user_id=test_user.id,
        note="Pending suggestion",
        status=SuggestionStatus.PENDING,
        is_active=True,
        created_at=func.now(),
        updated_at=func.now(),
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)
    return suggestion


@pytest_asyncio.fixture(scope="function")
async def test_suggestion_approved(db_session: AsyncSession, test_coin, test_user):
    """Fixture for an approved suggestion owned by test_user."""
    suggestion = Suggestion(
        id=uuid.uuid4(),
        coin_id=test_coin.id,
        user_id=test_user.id,
        note="Approved suggestion",
        status=SuggestionStatus.APPROVED,
        is_active=True,
        created_at=func.now(),
        updated_at=func.now(),
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)
    return suggestion