import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.security import create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.coin import Coin
from app.models.metric import Metric
from app.models.scoring_weight import ScoringWeight
from app.models.user import User, UserRole


# ✅ Configure logging using central setup
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    configure_logging()


###############################################################################
#                               DATABASE SETUP
###############################################################################


# Create async engine for testing
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Create an async sessionmaker bound to the test engine
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """
    Creates all tables at the start of the test session, drops them at the end.
    Ensures a fresh schema for tests.
    """
    async with engine.begin() as conn:
        print("🔄 [init_test_db] Creating all tables for test...")
        await conn.run_sync(Base.metadata.create_all)

    yield  # Run all tests

    async with engine.begin() as conn:
        print("🧹 [init_test_db] Dropping all tables after test session...")
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Creates a fresh test database session per test function."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


###############################################################################
#                     DB CLEANUP PER TEST (KEY PART)
###############################################################################
@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(db_session: AsyncSession):
    """
    Truncate all tables before each test to ensure a clean DB.
    This fixture runs automatically (autouse=True) for every test function.
    """
    tables = [
        "coins",
        "metrics",
        "scores",
        "scoring_weights",
        "suggestions",
        "user_activities",
        "users",
    ]
    for table in tables:
        await db_session.execute(
            text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
        )
    await db_session.commit()


###############################################################################
#                     OVERRIDE FastAPI's get_db DEPENDENCY
###############################################################################


@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_get_db():
    """
    Override FastAPI's `get_db` dependency once per test session so that
    all routes use the test DB sessionmaker instead of the real DB.
    """

    async def _get_test_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


###############################################################################
#                          IN-PROCESS TEST CLIENT
###############################################################################


@pytest_asyncio.fixture(scope="session")
async def client(init_test_db, override_get_db):
    """
    Provides an in-process client for testing, powered by:
      - asgi-lifespan (to run startup/shutdown)
      - httpx.ASGITransport (to send requests in-memory to the app)
    """
    async with LifespanManager(app):
        # ASGITransport routes requests directly to the in-memory FastAPI app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac


@pytest_asyncio.fixture(scope="function")
async def unauthorized_client(init_test_db, override_get_db):
    """
    Provides an in-process client with NO Authorization header.
    Useful for testing endpoints that require or forbid auth.
    """
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            ac.headers.pop("Authorization", None)
            yield ac


###############################################################################
#                               TEST FIXTURES
###############################################################################


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    """Creates and returns a unique test user per test function."""
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


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client, test_user):
    """Provides a client already authenticated with the given test_user."""
    access_token = create_access_token({"sub": str(test_user.id)})
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest_asyncio.fixture(scope="function")
async def manager_client(client: AsyncClient, db_session: AsyncSession):
    """
    Creates a fresh MANAGER user and logs them in to the in-process test client.
    """
    # Clear any old users
    await db_session.execute(delete(User))
    await db_session.commit()

    unique_email = f"manager_{uuid.uuid4().hex[:8]}@example.com"

    # Register a manager
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "testpassword",
            "name": "Test Manager",
            "role": "manager",
        },
    )
    assert register_response.status_code == 201, register_response.text

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": "testpassword"},
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest_asyncio.fixture(scope="function")
async def test_coin(db_session):
    """Creates a single test coin and returns it."""
    unique_symbol = f"TEST_{uuid.uuid4().hex[:6]}"
    unique_id = uuid.uuid4()
    coin = Coin(
        id=unique_id,
        coingeckoid=unique_symbol,
        name=unique_symbol,
        symbol=unique_symbol,
        description="coin for testing",
        github="https://github.com/onlycoinfortesting",
        is_active=True,
    )
    db_session.add(coin)
    await db_session.commit()
    await db_session.refresh(coin)
    return coin


@pytest_asyncio.fixture(scope="function")
async def test_coins(db_session):
    """Creates multiple test coins and returns them as a list of Coin objects."""
    coin_data_list = [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "description": "Bitcoin (BTC) is a cryptocurrency.",
            "github": "https://github.com/bitcoin",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "description": "Ethereum (ETH) is a cryptocurrency.",
            "github": "https://github.com/ethereum",
        },
        {
            "id": "solana",
            "symbol": "sol",
            "name": "Solana",
            "description": "Solana (SOL) is a cryptocurrency.",
            "github": "https://github.com/solana-labs",
        },
    ]

    created_coins = []
    for raw in coin_data_list:
        coin = Coin(
            id=uuid.uuid4(),
            coingeckoid=raw["id"],
            name=raw["name"],
            symbol=raw["symbol"],
            description=raw["description"],
            github=raw["github"],
            is_active=True,
        )
        db_session.add(coin)
        created_coins.append(coin)

    await db_session.commit()
    # Refresh each coin so we get updated fields (e.g. auto-timestamps) from DB
    for coin in created_coins:
        await db_session.refresh(coin)

    return created_coins


@pytest_asyncio.fixture(scope="function")
async def test_metrics(db_session, test_coin):
    """Creates several metrics linked to a single coin."""
    metrics = []
    for _ in range(3):
        metric = Metric(
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
        db_session.add(metric)
        metrics.append(metric)

    await db_session.commit()
    for m in metrics:
        await db_session.refresh(m)

    return metrics


@pytest_asyncio.fixture(scope="function")
async def test_suggestion_pending(db_session, test_coin, test_user):
    """Creates a single test suggestion."""
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


@pytest_asyncio.fixture(scope="function")
async def test_suggestion_approved(db_session, test_coin, test_user):
    """Creates a single test suggestion."""
    from app.models.suggestion import Suggestion, SuggestionStatus

    suggestion = Suggestion(
        id=uuid.uuid4(),
        coin_id=test_coin.id,
        user_id=test_user.id,
        note="Test suggestion",
        status=SuggestionStatus.APPROVED,
        is_active=True,
    )
    db_session.add(suggestion)
    await db_session.commit()
    await db_session.refresh(suggestion)
    return suggestion


@pytest_asyncio.fixture(scope="function")
async def scoring_weight(db_session: AsyncSession):
    """Creates and returns a test scoring weight entry."""
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


###############################################################################
#                            OPTIONAL DEBUG FIXTURE
###############################################################################


@pytest_asyncio.fixture(scope="session", autouse=True)
async def debug_db(init_test_db):
    """
    Prints some debug info about the current DB/tables at the start of the test session.
    This runs after tables are created but before any test runs.
    """
    async with engine.connect() as conn:
        # Check current database
        result = await conn.execute(text("SELECT current_database();"))
        db_name = result.scalar()
        print(f"✅ Connected to database: {db_name}")

        # Check available tables
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"📌 Tables in database: {tables}")

        # Check structure of 'metrics' table
        result = await conn.execute(
            text(
                """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'metrics'
        """
            )
        )
        columns = result.fetchall()
        print(f"🛠 Metric table columns: {columns}")

    # We've already created tables in init_test_db, so just print info here.
    yield
    # init_test_db will drop tables after the session.
