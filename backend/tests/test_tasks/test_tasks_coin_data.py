import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.models import Coin
from app.tasks.coin_data import fetch_coin_data

@pytest.mark.asyncio(loop_scope="session")
async def test_fetch_coin_data(db_session: AsyncSession, mocker):
    """Test that fetch_coin_data fetches data and stores metrics."""

    # ✅ Mock API function returning valid data
    async def mock_fetch_coin_market_data(symbol):
        print(f"📡 Mock API called for {symbol}")  # Debugging
        return {
            "coingeckoid": "bitcoin",
            "market_cap": {"value": 1000000, "currency": "USD"},
            "volume_24h": {"value": 500000, "currency": "USD"},
            "liquidity": {"value": 200000, "currency": "USD"},
            "github_activity": 10,
            "twitter_sentiment": 0.8,
            "reddit_sentiment": 0.9,
            "fetched_at": "2025-03-16T12:00:00Z"
        }

    # ✅ Mock the API client correctly
    mocker.patch(
        "app.utils.api_clients.coingecko.fetch_coin_market_data",
        side_effect=mock_fetch_coin_market_data
    )

    print("✅ Mock API response set.")

    # ✅ Clear database to prevent conflicts
    await db_session.execute(text("DELETE FROM metrics"))
    await db_session.execute(text("DELETE FROM coins WHERE symbol = 'BTC'"))
    await db_session.commit()

    coin_id = uuid.uuid4()

    # ✅ Insert a mock coin
    new_coin = Coin(
        id=coin_id,
        symbol="bitcoin",  # ✅ Ensure symbol matches mock data
        name="Bitcoin",
        coingeckoid="bitcoin",
        is_active=True
    )
    db_session.add(new_coin)
    await db_session.commit()
    await db_session.refresh(new_coin)  # ✅ Ensure DB session sees the coin

    print(f"✅ Inserted mock coin: {coin_id}")

    # ✅ Run the function under test
    await fetch_coin_data(db_session)
    await db_session.commit()  # ✅ Ensure changes are flushed

    print("✅ fetch_coin_data() executed.")

    # ✅ Verify that a metric was stored
    result = await db_session.execute(
        text("SELECT * FROM metrics WHERE coin_id = :coin_id"),
        {"coin_id": coin_id}
    )
    metrics = result.fetchall()

    print(f"🔍 Metrics found: {metrics}")

    # ✅ Ensure at least one metric is found
    assert len(metrics) > 0, f"❌ Expected at least 1 metric, but found {len(metrics)}"
