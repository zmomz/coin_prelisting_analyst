import pytest
import uuid
import logging
import asyncio
from decouple import config
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from httpx import AsyncClient
from contextlib import asynccontextmanager
from app.db.session import AsyncSessionLocalTest
from datetime import datetime

from app.db.base import Base
from app.db.session import get_db_test
from app.main import app
from app.core.security import create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.metric import Metric
from app.models.scoring_weight import ScoringWeight


# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Override settings for testing
settings.SECRET_KEY = config("SECRET_KEY")
settings.DATABASE_URL = config("TEST_DATABASE_URL")
settings.REDIS_URL = config("REDIS_URL")
settings.CELERY_BROKER_URL = config("CELERY_BROKER_URL")
settings.CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND")
settings.GITHUB_TOKEN = config("GITHUB_TOKEN")
settings.TWITTER_BEARER_TOKEN = config("TWITTER_BEARER_TOKEN")
settings.REDDIT_CLIENT_ID = config("REDDIT_CLIENT_ID")
settings.REDDIT_CLIENT_SECRET = config("REDDIT_CLIENT_SECRET")
settings.REDDIT_USER_AGENT = config("REDDIT_USER_AGENT")
settings.SLACK_WEBHOOK_URL = config("SLACK_WEBHOOK_URL")

# Create async engine for testing
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure test database is set up before running tests."""
    async with engine.begin() as conn:
        print("🔄 Initializing Test Database...")
        await conn.run_sync(Base.metadata.create_all)

    await asyncio.sleep(1)  # ✅ Give the database time to initialize

    yield  # ✅ Run tests

    async with engine.begin() as conn:
        print("🧹 Cleaning Up Test Database...")
        await conn.run_sync(Base.metadata.drop_all)


# Attach lifespan to FastAPI instance
app = FastAPI(lifespan=lifespan)  # noqa


# ✅ Ensure a consistent event loop across all tests
@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # ✅ Explicitly set this loop as default
    yield loop
    loop.close()


# ✅ Keep database session scoped to **function** for test isolation
@pytest.fixture(scope="function")
async def db_session():
    """Creates a fresh database session per test."""
    async with AsyncSessionLocalTest() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()  # ✅ Rollback on failure
            raise e
        finally:
            await session.close()  # ✅ Ensure session is closed properly


# ✅ Override FastAPI's `get_db_test` once for all tests
@pytest.fixture(scope="session")
async def override_get_db_test():
    """Override FastAPI's `get_db_test` dependency with test session."""
    async def _get_test_db():
        async with AsyncSessionLocalTest() as session:
            yield session

    app.dependency_overrides[get_db_test] = _get_test_db
    yield
    app.dependency_overrides.clear()


# ✅ Keep client session-wide to improve performance
@pytest.fixture(scope="session")
async def client():
    """Provides an async HTTP client for testing."""
    async with AsyncClient(base_url="http://127.0.0.1:8000", timeout=30) as ac:
        yield ac


@pytest.fixture(scope="function")
async def unauthorized_client():
    """Fixture for an unauthenticated
    client (ensures no Authorization header)."""
    async with AsyncClient(base_url="http://127.0.0.1:8000") as client:
        client.headers.pop("Authorization", None)  # Ensure no auth header
        yield client


# ✅ Make test_user function-scoped for test isolation
@pytest.fixture(scope="function")
async def test_user(db_session):
    """Creates a unique test user per test."""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        id=uuid.uuid4(),
        email=unique_email,
        hashed_password=get_password_hash("testpass"),
        name="Test User",
        role=UserRole.ANALYST,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


# ✅ Ensure authenticated client is fresh per test
@pytest.fixture(scope="function")
async def authenticated_client(client, test_user):
    """Creates an authenticated client with a test user."""
    access_token = create_access_token({"sub": str(test_user.id)})
    client.headers = {"Authorization": f"Bearer {access_token}"}
    return client


# ✅ Manager client should be fresh per test
@pytest.fixture(scope="function")
async def manager_client(client: AsyncClient, db_session: AsyncSession):
    """Authenticated test client with a MANAGER role."""
    await db_session.execute(delete(User))
    await db_session.commit()

    unique_email = f"manager_{uuid.uuid4().hex[:8]}@example.com"

    response = await client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "testpassword",
              "name": "Test Manager", "role": "manager"},
    )
    assert response.status_code == 201, response.text

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword"},
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


# ✅ Test coins should be function-scoped for isolation
@pytest.fixture(scope="function")
async def test_coin(db_session):
    """Creates a test coin."""
    from app.models.coin import Coin

    coin = Coin(
        id=uuid.uuid4(),
        name="Test Coin",
        symbol=f"TEST{uuid.uuid4().hex[:4]}",
        description="A test coin for testing",
        github="https://github.com/test/test",
        is_active=True,
    )
    db_session.add(coin)
    await db_session.commit()
    await db_session.refresh(coin)
    return coin


@pytest.fixture(scope="function")
async def test_coins(db_session):
    """Creates multiple test coins."""
    from app.models.coin import Coin

    coins = []
    for i in range(3):
        coin = Coin(
            id=uuid.uuid4(),
            name=f"Test Coin {i}",
            symbol=f"TEST{i}{uuid.uuid4().hex[:4]}",
            description=f"A test coin {i} for testing",
            github=f"https://github.com/test/test{i}",
            is_active=True,
        )
        db_session.add(coin)
        coins.append(coin)

    await db_session.commit()
    for coin in coins:
        await db_session.refresh(coin)

    return coins


@pytest.fixture
async def test_metrics(db_session, test_coin):
    """Fixture to create test metrics."""
    metrics = [
        Metric(
            id=uuid.uuid4(),
            coin_id=test_coin.id,
            market_cap={"value": 1000000, "currency": "USD"},
            volume_24h={"value": 50000, "currency": "USD"},
            liquidity={"value": 100000, "currency": "USD"},
            github_activity={"count": 10},
            twitter_sentiment={"score": 0.8},
            reddit_sentiment={"score": 0.9},
            fetched_at=datetime.now(),
            is_active=True,
            created_at=datetime.now(),
        )
        for _ in range(3)
    ]

    db_session.add_all(metrics)
    await db_session.commit()
    await db_session.flush()

    return metrics


@pytest.fixture(scope="function")
async def test_suggestion(db_session, test_coin, test_user):
    """Creates a test suggestion."""
    from app.models.suggestion import Suggestion, SuggestionStatus

    suggestion = Suggestion(
        id=uuid.uuid4(),
        coin_id=test_coin.id,
        user_id=test_user.id,
        note="Test suggestion",
        status=SuggestionStatus.PENDING,
        is_active=True,
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)
    return suggestion


@pytest.fixture
async def scoring_weight(db_session: AsyncSession):
    """Fixture to create a test scoring weight entry."""
    weight = ScoringWeight(
        liquidity_score=0.3,
        developer_score=0.2,
        community_score=0.2,
        market_score=0.3,
    )
    db_session.add(weight)
    await db_session.commit()
    await db_session.refresh(weight)
    return weight
