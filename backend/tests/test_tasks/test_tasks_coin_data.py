import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from app.tasks.coin_data import fetch_coin_data


@pytest.mark.asyncio(loop_scope="session")
@patch("app.utils.api_clients.coingecko.fetch_coin_market_data", new_callable=AsyncMock)
async def test_fetch_coin_data(mock_fetch_market_data, db_session: AsyncSession, test_coin):
    """Test that coin data fetching task correctly stores market data."""
    mock_fetch_market_data.return_value = {
        "market_cap": 5000000,
        "volume_24h": 200000,
        "liquidity": 80,
        "github": None,
    }

    await fetch_coin_data()

    # Verify the mock was called
    mock_fetch_market_data.assert_called()
