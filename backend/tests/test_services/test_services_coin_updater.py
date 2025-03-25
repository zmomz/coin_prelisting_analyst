import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.services.coin_updater import update_coin_and_metrics_from_coingecko
from app.models.coin import Coin


@pytest_asyncio.fixture
def mock_coin_data():
    return {
        "id": "testcoin",
        "symbol": "tst",
        "name": "Test Coin",
        "description": {"en": "A test cryptocurrency"},
        "links": {
            "repos_url": {"github": ["https://github.com/test"]},
            "twitter_screen_name": "test_twitter",
            "subreddit_url": "https://reddit.com/r/test",
            "telegram_channel_identifier": "test_channel",
            "homepage": ["https://testcoin.org"]
        },
        "market_data": {
            "market_cap": {"usd": 12345.67},
            "total_volume": {"usd": 789.01},
            "liquidity_score": 42.0
        },
        "community_data": {
            "twitter_followers": 1337.0,
            "reddit_average_posts_48h": 3.14
        },
        "developer_data": {
            "commit_count_4_weeks": 27.0
        }
    }


@pytest.mark.asyncio
@patch("app.services.coin_updater.create_metric", new_callable=AsyncMock)
@patch("app.services.coin_updater.get_by_coingeckoid", new_callable=AsyncMock)
@patch("app.services.coin_updater.create_coin", new_callable=AsyncMock)
@patch("app.services.coin_updater.update_coin", new_callable=AsyncMock)
@patch("app.services.coin_updater.CoinGeckoClient")
async def test_update_coin_and_metrics_from_coingecko_create(
    mock_client_class,
    mock_update_coin,
    mock_create_coin,
    mock_get_by_coingeckoid,
    mock_create_metric,
    mock_coin_data,
    db_session,
):
    """
    Test case: Coin does not exist in DB.

    Expected behavior:
    - Fetch from CoinGecko
    - Create a new Coin and Metric entry
    - Do not call update_coin
    """
    # Setup mock CoinGecko client
    mock_client = AsyncMock()
    mock_client.get_coin_data.return_value = mock_coin_data
    mock_client_class.return_value = mock_client

    mock_get_by_coingeckoid.return_value = None

    mock_uuid = uuid4()
    mock_coin_obj = Coin(
        id=mock_uuid,
        coingeckoid="testcoin",
        name="Test Coin",
        symbol="TST",
    )
    mock_create_coin.return_value = mock_coin_obj

    result = await update_coin_and_metrics_from_coingecko(db_session, "testcoin")

    assert result is not None
    assert result.id == mock_uuid
    assert result.name == "Test Coin"
    mock_create_coin.assert_called_once()
    mock_create_metric.assert_called_once()
    mock_update_coin.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.coin_updater.create_metric", new_callable=AsyncMock)
@patch("app.services.coin_updater.get_by_coingeckoid", new_callable=AsyncMock)
@patch("app.services.coin_updater.create_coin", new_callable=AsyncMock)
@patch("app.services.coin_updater.update_coin", new_callable=AsyncMock)
@patch("app.services.coin_updater.CoinGeckoClient")
async def test_update_coin_and_metrics_from_coingecko_update(
    mock_client_class,
    mock_update_coin,
    mock_create_coin,
    mock_get_by_coingeckoid,
    mock_create_metric,
    mock_coin_data,
    db_session,
):
    """
    Test case: Coin already exists in DB.

    Expected behavior:
    - Fetch from CoinGecko
    - Update the Coin
    - Create a new Metric
    - Do not call create_coin
    """
    mock_client = AsyncMock()
    mock_client.get_coin_data.return_value = mock_coin_data
    mock_client_class.return_value = mock_client

    coin_uuid = uuid4()
    existing_coin = Coin(
        id=coin_uuid,
        coingeckoid="testcoin",
        name="Old Coin",
        symbol="TST",
    )
    updated_coin = Coin(
        id=coin_uuid,
        coingeckoid="testcoin",
        name="Test Coin",
        symbol="TST",
    )

    mock_get_by_coingeckoid.return_value = existing_coin
    mock_update_coin.return_value = updated_coin

    result = await update_coin_and_metrics_from_coingecko(db_session, "testcoin")

    assert result is not None
    assert result.id == coin_uuid
    assert result.name == "Test Coin"
    mock_update_coin.assert_called_once()
    mock_create_coin.assert_not_called()
    mock_create_metric.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.coin_updater.CoinGeckoClient")
async def test_update_coin_and_metrics_invalid_data(
    mock_client_class,
    db_session,
):
    """
    Test case: CoinGecko returns None (coin not found or API error).

    Expected behavior:
    - Return None
    - Do not raise exception
    """
    mock_client = AsyncMock()
    mock_client.get_coin_data.return_value = None
    mock_client_class.return_value = mock_client

    result = await update_coin_and_metrics_from_coingecko(db_session, "nonexistent")
    assert result is None
