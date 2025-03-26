import pytest
from uuid import uuid4
from unittest.mock import MagicMock

from app.services.scoringsync import (
    score_coin,
    calculate_component_scores,
    calculate_final_score,
    upsert_score,
)
from app.schemas.score import ScoreCreate
from app.models import Score


@pytest.fixture
def fake_metric():
    return MagicMock(
        liquidity=1000,
        github_activity=50,
        twitter_sentiment=0.5,
        reddit_sentiment=0.3,
        market_cap=50000000,
        volume_24h=25000000,
    )


@pytest.fixture
def fake_weights():
    return MagicMock(
        id=uuid4(),
        liquidity_score=0.25,
        developer_score=0.25,
        community_score=0.25,
        market_score=0.25,
    )


def test_calculate_component_scores(fake_metric):
    max_metrics = {
        "max_liquidity": 1000,
        "max_github_activity": 100,
        "max_community": 1,
        "max_market": 100000000,
    }

    scores = calculate_component_scores(fake_metric, max_metrics)

    assert scores["liquidity_score"] == 1
    assert scores["developer_score"] == 0.5
    assert scores["community_score"] == 0.8
    assert scores["market_score"] == 0.75


def test_calculate_final_score(fake_weights):
    components = {
        "liquidity_score": 1,
        "developer_score": 0.5,
        "community_score": 0.8,
        "market_score": 0.75,
    }

    final = calculate_final_score(components, fake_weights)
    expected = round((1 * 0.25 + 0.5 * 0.25 + 0.8 * 0.25 + 0.75 * 0.25), 4)
    assert final == expected


def test_upsert_score_create(mocker):
    db = MagicMock()
    db.query().filter().first.return_value = None

    score_in = ScoreCreate(
        coin_id=uuid4(),
        scoring_weight_id=uuid4(),
        liquidity_score=0.5,
        developer_score=0.6,
        community_score=0.7,
        market_score=0.8,
        final_score=0.65,
    )

    result = upsert_score(db, score_in)

    db.add.assert_called()
    db.commit.assert_called_once()
    assert isinstance(result, Score)


def test_upsert_score_update(mocker):
    db = MagicMock()
    existing = MagicMock(spec=Score)
    db.query().filter().first.return_value = existing

    score_in = ScoreCreate(
        coin_id=uuid4(),
        scoring_weight_id=uuid4(),
        liquidity_score=0.1,
        developer_score=0.2,
        community_score=0.3,
        market_score=0.4,
        final_score=0.25,
    )

    result = upsert_score(db, score_in)

    assert result == existing
    assert existing.liquidity_score == 0.1
    assert existing.final_score == 0.25
    db.add.assert_called_once_with(existing)
    db.commit.assert_called_once()


def test_score_coin_success(mocker, fake_metric, fake_weights):
    db = MagicMock()
    coin_id = uuid4()

    mocker.patch("app.services.scoringsync.get_latest_active_by_coin_sync", return_value=fake_metric)
    mocker.patch("app.services.scoringsync.find_max_metrics", return_value={
        "max_liquidity": 1000,
        "max_github_activity": 100,
        "max_community": 1,
        "max_market": 100000000,
    })
    mock_upsert = mocker.patch("app.services.scoringsync.upsert_score")

    score_coin(db, coin_id, fake_weights)

    mock_upsert.assert_called_once()
    args, _ = mock_upsert.call_args
    assert args[1].coin_id == coin_id
    assert 0 <= args[1].final_score <= 1


def test_score_coin_no_metric(mocker, fake_weights):
    db = MagicMock()
    coin_id = uuid4()

    mocker.patch("app.services.scoringsync.get_latest_active_by_coin_sync", return_value=None)
    upsert_mock = mocker.patch("app.services.scoringsync.upsert_score")

    score_coin(db, coin_id, fake_weights)

    upsert_mock.assert_not_called()
