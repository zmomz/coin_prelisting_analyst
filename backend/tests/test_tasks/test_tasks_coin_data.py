import pytest
from unittest.mock import patch, MagicMock

from app.tasks.coin_data import fetch_and_update_all_coins


@pytest.fixture
def patch_client():
    with patch("app.tasks.coin_data.SyncCoinGeckoClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        yield mock_client


@pytest.fixture
def patch_session(mocker):
    # Patch DB session
    return mocker.patch("app.tasks.coin_data.SessionLocal")


@pytest.fixture
def patch_sleep(mocker):
    # Patch time.sleep to avoid delays during test
    return mocker.patch("app.tasks.coin_data.time.sleep", return_value=None)


def test_fetch_and_update_all_coins_success(patch_client, patch_session, patch_sleep, mocker):
    mocker.patch("app.tasks.coin_data.get_tracked_coins_sync", return_value=["bitcoin", "ethereum"])
    mock_update = mocker.patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko_sync")
    mock_update.side_effect = lambda db, coin_id, coingecko_client: MagicMock(name=coin_id.capitalize())

    fetch_and_update_all_coins()

    assert mock_update.call_count == 2
    mock_update.assert_any_call(patch_session.return_value, "bitcoin", coingecko_client=patch_client)
    mock_update.assert_any_call(patch_session.return_value, "ethereum", coingecko_client=patch_client)


def test_fetch_and_update_all_coins_no_tracked(patch_client, patch_session, mocker):
    mocker.patch("app.tasks.coin_data.get_tracked_coins_sync", return_value=[])

    # Should return early with no updates
    fetch_and_update_all_coins()


def test_fetch_and_update_all_coins_coin_update_error(patch_client, patch_session, patch_sleep, mocker):
    mocker.patch("app.tasks.coin_data.get_tracked_coins_sync", return_value=["bitcoin", "ethereum"])

    def update_side_effect(db, coin_id, coingecko_client):
        if coin_id == "bitcoin":
            raise Exception("Update failed!")
        return MagicMock(name="Ethereum")

    mock_update = mocker.patch("app.tasks.coin_data.update_coin_and_metrics_from_coingecko_sync", side_effect=update_side_effect)

    fetch_and_update_all_coins()
    assert mock_update.call_count == 2


def test_fetch_and_update_all_coins_total_failure(patch_client, patch_session, mocker):
    # Fail on get_tracked_coins_sync
    mocker.patch("app.tasks.coin_data.get_tracked_coins_sync", side_effect=Exception("DB error"))

    fetch_and_update_all_coins()  # Should not raise
