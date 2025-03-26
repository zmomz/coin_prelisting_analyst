import pytest
from unittest.mock import MagicMock

from app.tasks.scoring_all import score_all_coins


@pytest.fixture
def patch_session(mocker):
    return mocker.patch("app.tasks.scoring_all.SessionLocal")


@pytest.fixture
def patch_score_coin(mocker):
    return mocker.patch("app.tasks.scoring_all.score_coin")


@pytest.fixture
def patch_logger(mocker):
    return mocker.patch("app.tasks.scoring_all.logger")


def test_score_all_coins_success(patch_session, patch_score_coin, mocker):
    fake_weight_id = "f890475c-ad0e-4b52-8cc2-ba3d02e5cacf"

    mock_weight = MagicMock()
    mock_coin_1 = MagicMock(id="coin1")
    mock_coin_2 = MagicMock(id="coin2")

    mocker.patch("app.tasks.scoring_all.getsync", return_value=mock_weight)
    mocker.patch("app.tasks.scoring_all.get_all_sync", return_value=[mock_coin_1, mock_coin_2])

    result = score_all_coins(scoring_weight_id=fake_weight_id)

    assert patch_score_coin.call_count == 2
    patch_score_coin.assert_any_call(patch_session.return_value, "coin1", mock_weight)
    patch_score_coin.assert_any_call(patch_session.return_value, "coin2", mock_weight)
    assert result == f"Scored 2 coins using ScoringWeight {fake_weight_id}"


def test_score_all_coins_weight_not_found(patch_session, mocker):
    fake_weight_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    mocker.patch("app.tasks.scoring_all.getsync", return_value=None)

    result = score_all_coins(scoring_weight_id=fake_weight_id)

    assert result == f"ScoringWeight {fake_weight_id} not found"


def test_score_all_coins_exception(patch_session, mocker):
    fake_weight_id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"

    mocker.patch("app.tasks.scoring_all.getsync", side_effect=Exception("DB failure"))
    db_instance = patch_session.return_value

    with pytest.raises(Exception, match="DB failure"):
        score_all_coins(scoring_weight_id=fake_weight_id)

    db_instance.rollback.assert_called_once()
    db_instance.close.assert_called_once()
