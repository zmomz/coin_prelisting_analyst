import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.services.coin_updater_sync import (
    update_coin_and_metrics_from_coingecko_sync,
    calculate_market_cap,
    calculate_volume,
    calculate_liquidity,
    calculate_github_activity,
    calculate_social_sentiment,
    extract_description,
    extract_link,
)


@pytest.fixture
def mock_db(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_coin_data():
    return {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "description": {"en": "Bitcoin is a cryptocurrency."},
        "links": {
            "repos_url": {"github": ["https://github.com/bitcoin/bitcoin"]},
            "homepage": ["https://bitcoin.org"],
            "twitter_screen_name": "bitcoin",
            "subreddit_url": "https://reddit.com/r/bitcoin",
            "telegram_channel_identifier": "bitcoin_channel",
        },
        "market_data": {
            "market_cap": {"usd": 500000000},
            "current_price": {"usd": 25000},
            "circulating_supply": 20000000,
            "total_volume": {"usd": 10000000},
        },
        "developer_data": {
            "commit_count_4_weeks": 50,
            "forks": 10,
            "stars": 100,
            "pull_requests_merged": 5,
            "last_4_weeks_commit_activity_series": [1] * 10,
            "total_issues": 15,
            "pull_request_contributors": 3,
        },
        "community_data": {
            "twitter_followers": 100000,
            "reddit_subscribers": 150000,
            "reddit_average_posts_48h": 20,
            "reddit_accounts_active_48h": 500,
            "reddit_average_comments_48h": 100,
        },
        "tickers": [{"converted_volume": {"usd": 100000}}],
    }


def test_update_coin_and_metrics_success(mock_db, mock_client, mock_coin_data, mocker):
    mock_client.get_coin_data.return_value = mock_coin_data

    mocker.patch("app.services.coin_updater_sync.get_by_coingeckoid_sync", return_value=None)

    # ✅ Proper mock object with attributes, not a MagicMock return_value with internal name
    mock_coin = MagicMock()
    mock_coin.id = uuid4()
    mock_coin.name = "Bitcoin"
    mocker.patch("app.services.coin_updater_sync.create_coin_sync", return_value=mock_coin)

    mocker.patch("app.services.coin_updater_sync.create_metric_sync")

    coin = update_coin_and_metrics_from_coingecko_sync(mock_db, "bitcoin", coingecko_client=mock_client)

    assert coin.name == "Bitcoin"
    mock_client.get_coin_data.assert_called_once_with("bitcoin")


def test_update_coin_and_metrics_invalid_data(mock_db, mock_client, mocker):
    mock_client.get_coin_data.return_value = {}

    coin = update_coin_and_metrics_from_coingecko_sync(mock_db, "invalidcoin", coingecko_client=mock_client)

    assert coin is None


# -------------------------------
# Unit tests for individual functions
# -------------------------------

def test_calculate_market_cap_direct():
    data = {
        "market_data": {
            "market_cap": {"usd": 1000000},
            "current_price": {"usd": 100},
            "circulating_supply": 10000,
            "total_volume": {"usd": 10000}
        }
    }
    assert calculate_market_cap(data) == 1000000


def test_calculate_market_cap_fallback():
    data = {
        "market_data": {
            "current_price": {"usd": 100},
            "circulating_supply": 10000
        }
    }
    assert calculate_market_cap(data) == 1000000


def test_calculate_volume_direct():
    data = {"market_data": {"total_volume": {"usd": 200000}}}
    assert calculate_volume(data) == 200000


def test_calculate_liquidity():
    assert calculate_liquidity(1000000, 10000) > 0


def test_calculate_github_activity():
    data = {
        "developer_data": {
            "commit_count_4_weeks": 50,
            "forks": 20,
            "stars": 100,
            "pull_requests_merged": 5,
            "last_4_weeks_commit_activity_series": [1] * 10,
            "total_issues": 30,
            "pull_request_contributors": 3
        }
    }
    result = calculate_github_activity(data)
    assert result > 0


def test_calculate_social_sentiment():
    data = {
        "community_data": {
            "twitter_followers": 100000,
            "reddit_subscribers": 50000,
            "reddit_average_posts_48h": 5,
            "reddit_accounts_active_48h": 100,
            "reddit_average_comments_48h": 50
        }
    }
    twitter, reddit = calculate_social_sentiment(data)
    assert twitter > 0
    assert reddit > 0


def test_extract_description():
    data = {"description": {"en": "Test description"}}
    assert extract_description(data) == "Test description"


def test_extract_link_from_list():
    data = {"links": {"homepage": ["https://example.com"]}}
    result = extract_link(data, [["links", "homepage"]])
    assert result == "https://example.com"


def test_extract_link_from_string():
    data = {"links": {"subreddit_url": "https://reddit.com/r/test"}}
    result = extract_link(data, [["links", "subreddit_url"]])
    assert result == "https://reddit.com/r/test"
