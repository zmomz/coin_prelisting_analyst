import pytest
from unittest.mock import AsyncMock, patch
from app.utils.api_clients.coingecko import fetch_coin_market_data
from app.utils.api_clients.github import fetch_github_activity
from app.utils.api_clients.twitter import fetch_twitter_sentiment
from app.utils.api_clients.reddit import fetch_reddit_sentiment


@pytest.mark.asyncio(loop_scope="session")
@patch("app.utils.api_clients.coingecko.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_coin_market_data_api_failure(mock_get):
    """Test CoinGecko API failure handling."""
    mock_get.return_value.status_code = 500  # Simulating API failure

    result = await fetch_coin_market_data("btc")
    assert result is None  # Ensure function handles API failures gracefully


@pytest.mark.asyncio(loop_scope="session")
@patch("app.utils.api_clients.github.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_github_activity_api_failure(mock_get):
    """Test GitHub API failure handling."""
    mock_get.return_value.status_code = 403  # Simulating rate limit

    result = await fetch_github_activity("https://github.com/org/repo")
    assert result is None  # Ensure function handles API failures properly


@pytest.mark.asyncio(loop_scope="session")
@patch("app.utils.api_clients.twitter.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_twitter_sentiment_api_failure(mock_get):
    """Test Twitter API failure handling."""
    mock_get.return_value.status_code = 401  # Simulating authentication failure

    result = await fetch_twitter_sentiment("elonmusk")
    assert result is None  # Ensure function handles API failures properly


@pytest.mark.asyncio(loop_scope="session")
@patch("app.utils.api_clients.reddit.httpx.AsyncClient.get", new_callable=AsyncMock)
async def test_fetch_reddit_sentiment_api_failure(mock_get):
    """Test Reddit API failure handling."""
    mock_get.return_value.status_code = 404  # Simulating missing subreddit

    result = await fetch_reddit_sentiment("nonexistentsubreddit")
    assert result is None  # Ensure function handles API failures properly
