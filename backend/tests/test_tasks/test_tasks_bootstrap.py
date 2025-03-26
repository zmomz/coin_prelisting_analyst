import pytest
from unittest.mock import MagicMock, patch

from app.tasks.bootstrap import bootstrap_supported_coins
from app.schemas.coin import CoinCreate
from app.db.session import SessionLocal
from sqlalchemy import text


@pytest.fixture(autouse=True)
def clean_db():
    """Clean up tables before each test run."""
    db = SessionLocal()
    tables = [
        "coins", "metrics", "scores", "scoring_weights",
        "suggestions", "user_activities", "users"
    ]
    for table in tables:
        db.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
    db.commit()
    db.close()


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def mock_supported_coins():
    return [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        {"id": "incomplete_coin"},  # Should be skipped
    ]


@pytest.fixture
def patch_client(mock_supported_coins):
    with patch("app.tasks.bootstrap.SyncCoinGeckoClient") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.get_supported_coins.return_value = mock_supported_coins
        mock_client_cls.return_value = mock_client
        yield mock_client


@pytest.fixture
def patch_crud(mocker):
    mocker.patch("app.tasks.bootstrap.get_all_coingeckoids_sync", return_value=["bitcoin"])
    return mocker.patch("app.tasks.bootstrap.create_coin_sync")


def test_bootstrap_supported_coins_success(patch_client, patch_crud, db_session):
    bootstrap_supported_coins()

    # Should insert Ethereum only, since Bitcoin already exists, and the last one is invalid
    patch_crud.assert_called_once()
    args, kwargs = patch_crud.call_args
    assert isinstance(args[1], CoinCreate)
    assert args[1].coingeckoid == "ethereum"
    assert args[1].symbol == "ETH"
    assert args[1].name == "Ethereum"
    assert args[1].is_active is True


def test_bootstrap_skips_invalid_entries(patch_client, patch_crud, db_session):
    bootstrap_supported_coins()

    # Only 1 coin should be inserted (Ethereum), 1 duplicate (Bitcoin), 1 invalid skipped
    assert patch_crud.call_count == 1


def test_bootstrap_handles_insert_exception(patch_client, mocker, db_session):
    # Patch `create_coin_sync` to raise an exception
    mock_create = mocker.patch("app.tasks.bootstrap.create_coin_sync", side_effect=Exception("DB error"))
    bootstrap_supported_coins()
    # All valid new coins attempted, but raised exceptions
    assert mock_create.call_count == 2


def test_bootstrap_handles_total_failure(mocker):
    # Force failure in `get_supported_coins`
    mocker.patch("app.tasks.bootstrap.SyncCoinGeckoClient.get_supported_coins", side_effect=Exception("API Down"))
    with patch("app.tasks.bootstrap.SyncCoinGeckoClient.close"):
        bootstrap_supported_coins()  # Should not raise
