import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.tasks.bootstrap import _bootstrap_supported_coins


@pytest_asyncio.fixture
def fake_supported_coins():
    return [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        {"id": "cardano", "symbol": "ada", "name": "Cardano"},
    ]


@pytest.mark.asyncio
@patch("app.tasks.bootstrap.fetch_and_update_all_coins")
@patch("app.tasks.bootstrap.create_coin", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.get_all_coingeckoids", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.CoinGeckoClient")
async def test_bootstrap_supported_coins_creates_new_coins(
    mock_client_class,
    mock_get_existing,
    mock_create_coin,
    mock_followup_task,
    fake_supported_coins,
):
    """
    ✅ Test that new coins returned from CoinGecko are inserted into the database
    if they do not already exist.
    """
    mock_client = AsyncMock()
    mock_client.get_supported_coins.return_value = fake_supported_coins
    mock_client.close = AsyncMock()
    mock_client_class.return_value = mock_client

    mock_get_existing.return_value = ["bitcoin"]

    await _bootstrap_supported_coins()

    assert mock_create_coin.await_count == 2  # ethereum, cardano
    mock_followup_task.delay.assert_called_once()
    mock_client.close.assert_awaited()


@pytest.mark.asyncio
@patch("app.tasks.bootstrap.fetch_and_update_all_coins")
@patch("app.tasks.bootstrap.create_coin", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.get_all_coingeckoids", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.CoinGeckoClient")
async def test_bootstrap_supported_coins_skips_existing_coins(
    mock_client_class,
    mock_get_existing,
    mock_create_coin,
    mock_followup_task,
    fake_supported_coins,
):
    """
    ✅ Test that if all coins already exist in the database, no new coins are inserted.
    """
    mock_client = AsyncMock()
    mock_client.get_supported_coins.return_value = fake_supported_coins
    mock_client.close = AsyncMock()
    mock_client_class.return_value = mock_client

    mock_get_existing.return_value = ["bitcoin", "ethereum", "cardano"]

    await _bootstrap_supported_coins()

    mock_create_coin.assert_not_awaited()
    mock_followup_task.delay.assert_called_once()
    mock_client.close.assert_awaited()


@pytest.mark.asyncio
@patch("app.tasks.bootstrap.fetch_and_update_all_coins")
@patch("app.tasks.bootstrap.create_coin", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.get_all_coingeckoids", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.CoinGeckoClient")
async def test_bootstrap_supported_coins_handles_empty_list(
    mock_client_class,
    mock_get_existing,
    mock_create_coin,
    mock_followup_task,
):
    """
    ✅ Test that if CoinGecko returns an empty list, no insertion is attempted and
    follow-up tasks are not triggered.
    """
    mock_client = AsyncMock()
    mock_client.get_supported_coins.return_value = []
    mock_client.close = AsyncMock()
    mock_client_class.return_value = mock_client

    mock_get_existing.return_value = []

    await _bootstrap_supported_coins()

    mock_create_coin.assert_not_awaited()
    mock_followup_task.delay.assert_called_once()
    mock_client.close.assert_awaited()


@pytest.mark.asyncio
@patch("app.tasks.bootstrap.fetch_and_update_all_coins")
@patch("app.tasks.bootstrap.create_coin", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.get_all_coingeckoids", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.CoinGeckoClient")
async def test_bootstrap_supported_coins_handles_exception(
    mock_client_class,
    mock_get_existing,
    mock_create_coin,
    mock_followup_task,
):
    """
    ✅ Test that the task handles exceptions gracefully if CoinGecko API fails.
    """
    mock_client = AsyncMock()
    mock_client.get_supported_coins.side_effect = Exception("CoinGecko is down")
    mock_client.close = AsyncMock()
    mock_client_class.return_value = mock_client

    await _bootstrap_supported_coins()

    mock_create_coin.assert_not_awaited()
    mock_followup_task.delay.assert_not_called()
    mock_client.close.assert_awaited()


@pytest.mark.asyncio
@patch("app.tasks.bootstrap.fetch_and_update_all_coins")
@patch("app.tasks.bootstrap.create_coin", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.get_all_coingeckoids", new_callable=AsyncMock)
@patch("app.tasks.bootstrap.CoinGeckoClient")
async def test_bootstrap_supported_coins_partial_failure(
    mock_client_class,
    mock_get_existing,
    mock_create_coin,
    mock_followup_task,
    fake_supported_coins,
):
    """
    🧪 Optional: Test partial insert where some coins succeed and some fail.
    """
    mock_client = AsyncMock()
    mock_client.get_supported_coins.return_value = fake_supported_coins
    mock_client.close = AsyncMock()
    mock_client_class.return_value = mock_client

    mock_get_existing.return_value = []

    async def side_effect(db, coin_data):
        if coin_data.name == "Ethereum":
            raise Exception("Insert fail")
        return MagicMock()

    mock_create_coin.side_effect = side_effect

    await _bootstrap_supported_coins()

    assert mock_create_coin.await_count == 3
    mock_followup_task.delay.assert_called_once()
    mock_client.close.assert_awaited()
