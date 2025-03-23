import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class DummyMetric:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.mark.asyncio
@patch("app.services.coin_updater.get_coins", new_callable=AsyncMock)
@patch("app.services.coin_updater.fetch_coin_market_data", new_callable=AsyncMock)
@patch("app.services.coin_updater.update_coin", new_callable=AsyncMock)
@patch("app.services.coin_updater.create_async_engine", new_callable=MagicMock)
async def test_update_all_coin_metrics(
    mock_create_engine,
    mock_update_coin,
    mock_fetch_data,
    mock_get_coins,
):
    with patch("app.services.coin_updater.Metric", new=DummyMetric):
        mock_get_coins.return_value = [
            type("Coin", (), {"id": 1, "symbol": "BTC", "coingeckoid": "bitcoin"})
        ]

        mock_fetch_data.return_value = {
            "market_cap": 1000,
            "total_volume": 200,
            "liquidity_score": 5,
            "developer_data": {"commit_count_4_weeks": 42},
            "sentiment_votes_up_percentage": 90.0,
            "sentiment_votes_down_percentage": 10.0,
            "description": "desc",
            "github": "https://github.com",
            "x": "https://x.com/test",
            "reddit": "https://reddit.com/r/test",
            "telegram": "https://t.me/test",
            "website": "https://coin.com"
        }

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session

        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_create_engine.return_value = mock_engine

        with patch("app.services.coin_updater.sessionmaker", return_value=mock_session_factory):
            from app.services.coin_updater import update_all_coin_metrics
            await update_all_coin_metrics()

        mock_get_coins.assert_awaited_once()
        mock_fetch_data.assert_awaited_once()
        mock_update_coin.assert_awaited_once()
        mock_session.commit.assert_awaited_once()
        mock_engine.dispose.assert_awaited_once()
