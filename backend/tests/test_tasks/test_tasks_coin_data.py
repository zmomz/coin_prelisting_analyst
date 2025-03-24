import types
from unittest.mock import patch

from app.tasks import coin_data


def test_fetch_coin_data_task():
    """Ensure Celery task calls update_all_coin_metrics via asyncio.run."""
    with patch("app.tasks.coin_data.asyncio.run") as mock_run:
        coin_data.fetch_coin_data()
        passed_coro = mock_run.call_args[0][0]

        assert isinstance(passed_coro, types.CoroutineType)
        assert passed_coro.__name__ == "update_all_coin_metrics"
        mock_run.assert_called_once()

        passed_coro.close()


def test_update_coins_list_task():
    """Ensure Celery task calls update_coin_list via asyncio.run."""
    with patch("app.tasks.coin_data.asyncio.run") as mock_run:
        coin_data.update_coins_list()
        passed_coro = mock_run.call_args[0][0]

        assert isinstance(passed_coro, types.CoroutineType)
        assert passed_coro.__name__ == "update_coin_list"
        mock_run.assert_called_once()

        passed_coro.close()
