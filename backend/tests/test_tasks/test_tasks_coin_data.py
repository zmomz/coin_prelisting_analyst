import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, call, MagicMock
from app.tasks.coin_data import _fetch_and_update_all_coins


@pytest_asyncio.fixture
def tracked_coins():
    return ["bitcoin", "ethereum", "cardano"]


@pytest.mark.asyncio
@patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko", new_callable=AsyncMock)
@patch("app.tasks.coin_data.get_tracked_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.CoinGeckoClient", autospec=True)
async def test_fetch_and_update_all_coins_success(
    mock_client_class,
    mock_get_tracked_coins,
    mock_update,
    tracked_coins
):
    """✅ Test all tracked coins are updated successfully when returned by DB."""
    mock_get_tracked_coins.return_value = tracked_coins
    mock_update.return_value = MagicMock(name="MockCoin", name_attr="Bitcoin")

    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    await _fetch_and_update_all_coins()

    assert mock_update.await_count == len(tracked_coins)
    assert mock_client_instance.close.await_count == 1


@pytest.mark.asyncio
@patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko", new_callable=AsyncMock)
@patch("app.tasks.coin_data.get_tracked_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.CoinGeckoClient", autospec=True)
async def test_fetch_and_update_all_coins_empty_list(
    mock_client_class,
    mock_get_tracked_coins,
    mock_update,
):
    """✅ Test task does nothing if no tracked coins are found."""
    mock_get_tracked_coins.return_value = []
    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    await _fetch_and_update_all_coins()

    mock_update.assert_not_awaited()
    mock_client_instance.close.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko", new_callable=AsyncMock)
@patch("app.tasks.coin_data.get_tracked_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.CoinGeckoClient", autospec=True)
async def test_fetch_and_update_all_coins_partial_failure(
    mock_client_class,
    mock_get_tracked_coins,
    mock_update,
    tracked_coins
):
    """🧪 Test partial update: some coins succeed, some fail."""
    mock_get_tracked_coins.return_value = tracked_coins

    async def side_effect(db, coin_id, coingecko_client=None):
        if coin_id == "ethereum":
            raise Exception("Rate limit hit")
        return MagicMock(name=coin_id)

    mock_update.side_effect = side_effect
    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    await _fetch_and_update_all_coins()

    assert mock_update.await_count == len(tracked_coins)
    assert mock_client_instance.close.await_count == 1


@pytest.mark.asyncio
@patch("app.tasks.coin_data.get_tracked_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.CoinGeckoClient", autospec=True)
async def test_fetch_and_update_all_coins_top_level_exception(
    mock_client_class,
    mock_get_tracked_coins,
):
    """🧪 Test task handles top-level exception gracefully (e.g., DB failure)."""
    mock_get_tracked_coins.side_effect = Exception("DB error")
    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    await _fetch_and_update_all_coins()
    # No assert needed, just verifying no crash


@pytest.mark.asyncio
@patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko", new_callable=AsyncMock)
@patch("app.tasks.coin_data.get_tracked_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.CoinGeckoClient", autospec=True)
async def test_fetch_and_update_all_coins_rate_limiting_sleep(
    mock_client_class,
    mock_get_tracked_coins,
    mock_update,
    tracked_coins,
    monkeypatch
):
    """✅ Ensure asyncio.sleep(1) is awaited per coin to respect rate limits."""
    mock_get_tracked_coins.return_value = tracked_coins
    mock_update.return_value = MagicMock(name="Bitcoin")

    mock_client_instance = AsyncMock()
    mock_client_class.return_value = mock_client_instance

    sleep_mock = AsyncMock()
    monkeypatch.setattr("app.tasks.coin_data.asyncio.sleep", sleep_mock)

    await _fetch_and_update_all_coins()

    assert sleep_mock.await_count == len(tracked_coins)
    sleep_mock.assert_has_calls([call(1) for _ in tracked_coins])
    assert mock_client_instance.close.await_count == 1
