import pytest
import asyncio
from unittest.mock import patch, AsyncMock

# Import the tasks from your code
# Adjust the import paths as needed for your project structure
from app.tasks.coin_data import update_coins_list, fetch_coin_data, _fetch_coin_data_async, process_coin_data


###############################################################################
# 1) Test the update_coins_list task
###############################################################################
@pytest.mark.asyncio(loop_scope="session")
@patch("app.tasks.coin_data.fetch_and_store_coins", new_callable=AsyncMock)
async def test_update_coins_list(mock_fetch_and_store_coins):
    """
    Test that 'update_coins_list' calls 'fetch_and_store_coins' internally
    and completes without error.
    """
    # Run the Celery task as if it were just a regular function
    update_coins_list()

    # Celery calls `asyncio.run(...)`, which in turn calls 'fetch_and_store_coins'
    # This test ensures the function is invoked.
    mock_fetch_and_store_coins.assert_awaited_once()


###############################################################################
# 2) Test the fetch_coin_data task
###############################################################################
@pytest.mark.asyncio(loop_scope="session")
@patch("app.tasks.coin_data._fetch_coin_data_async", new_callable=AsyncMock)
async def test_fetch_coin_data(mock_fetch_coin_data_async):
    """
    Test that 'fetch_coin_data' calls '_fetch_coin_data_async' internally
    and completes without error.
    """
    # Call the Celery task
    fetch_coin_data()

    # Inside the task, there's an asyncio.run(...) that calls _fetch_coin_data_async
    mock_fetch_coin_data_async.assert_awaited_once()


###############################################################################
# 3) (Optional) Test the internal _fetch_coin_data_async logic
###############################################################################
@pytest.mark.asyncio(loop_scope="session")
@patch("app.tasks.coin_data.get_coins", new_callable=AsyncMock)
@patch("app.tasks.coin_data.fetch_coin_market_data", new_callable=AsyncMock)
@patch("app.tasks.coin_data.Metric", autospec=True)
@patch("app.tasks.coin_data.datetime", autospec=True)
async def test__fetch_coin_data_async(
    mock_datetime,
    mock_Metric,
    mock_fetch_coin_market_data,
    mock_get_coins
):
    """
    Tests the main async function's logic:
      - It retrieves coins
      - Fetches market data for each
      - Calls process_coin_data
      - Creates Metric objects
      - Commits to the DB
    """
    # 1) Setup: mock the get_coins to return a list of "fake" coins
    mock_get_coins.return_value = [
        # Fake coin objects with minimal attributes
        type("Coin", (), {"id": 1, "symbol": "BTC", "coingeckoid": "bitcoin"}),
        type("Coin", (), {"id": 2, "symbol": "GIB", "coingeckoid": "_"}),
    ]

    # 2) Mock fetch_coin_market_data to return some pretend dictionary
    mock_fetch_coin_market_data.side_effect = [
        {"market_cap": 1234, "total_volume": 456, "liquidity_score": 10, "developer_data": {}, "sentiment_votes_up_percentage": 70.0},
        {}  # second call returns empty data for second coin
    ]

    # 3) datetime.utcnow() usage
    mock_datetime.utcnow.return_value = "FAKE_DATE"

    # 4) Actually call _fetch_coin_data_async:
    #    This function uses an ephemeral DB session, so we can't easily check the DB.
    #    Instead, we ensure no exceptions are raised and Metric objects are created.
    await _fetch_coin_data_async()

    # 5) Verify get_coins was called once
    mock_get_coins.assert_awaited_once()

    # 6) Verify fetch_coin_market_data was called as many times as there are coins
    assert mock_fetch_coin_market_data.await_count == 2

    # 7) Because the second coin’s market data is empty, process_coin_data returns None or partial data
    #    But the first coin should produce a Metric object
    #    Check how many times we tried to create a Metric instance:
    assert mock_Metric.call_count == 1, "Should only create a Metric for the coin that has data"

    # (Optional) We can also check the call args for the one Metric creation:
    first_call_args, _ = mock_Metric.call_args
    # first_call_args is a dict of the constructor’s parameters
    # For example: (coin_id=1, market_cap=..., volume_24h=..., liquidity=..., etc.)
    # So we can do partial checks:
    assert first_call_args["coin_id"] == 1
    assert first_call_args["market_cap"] == {"value": 1234, "currency": "USD"}


###############################################################################
# 4) (Optional) Test the process_coin_data helper
###############################################################################
def test_process_coin_data():
    """
    Unit test for the data processing logic that transforms raw API data
    into the expected metrics dictionary.
    """
    fake_data = {
        "market_cap": 1000,
        "total_volume": 250,
        "liquidity_score": 5,
        "developer_data": {"commit_count_4_weeks": 42},
        "sentiment_votes_up_percentage": 90.5,
        "sentiment_votes_down_percentage": 9.5
    }

    metrics = process_coin_data(fake_data)

    assert metrics["market_cap"] == {"value": 1000, "currency": "USD"}
    assert metrics["volume_24h"] == {"value": 250, "currency": "USD"}
    assert metrics["liquidity"]  == {"value": 5, "currency": "USD"}
    assert metrics["github_activity"] == 42
    assert metrics["twitter_sentiment"] == 90.5
    assert metrics["reddit_sentiment"]  == 9.5

    # If any of these fields are missing from the incoming data,
    # process_coin_data will fallback to zeros.


def test_process_coin_data_empty():
    """
    If the API returns an empty dict, process_coin_data should handle gracefully
    and return fields with 0/None defaults (not raise exceptions).
    """
    metrics = process_coin_data({})
    assert metrics["market_cap"] == {"value": 0, "currency": "USD"}
    assert metrics["volume_24h"] == {"value": 0, "currency": "USD"}
    assert metrics["liquidity"]  == {"value": 0, "currency": "USD"}
    assert metrics["github_activity"] == 0
    assert metrics["twitter_sentiment"] == 0.0
    assert metrics["reddit_sentiment"]  == 0.0
