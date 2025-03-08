import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.scoring import calculate_coin_score, update_coin_score
from app.crud.scores import get_score_by_coin
import uuid


@pytest.mark.asyncio
async def test_calculate_coin_score():
    """Test scoring algorithm with sample metrics."""
    metrics = {
        "market_cap": {"normalized": 0.8},
        "volume_24h": {"normalized": 0.6},
        "github_activity": {"normalized": 0.7},
        "twitter_sentiment": {"normalized": 0.5},
        "reddit_sentiment": {"normalized": 0.4},
    }
    score = await calculate_coin_score(metrics)
    assert 0 <= score <= 1  # Score should be within range


@pytest.mark.asyncio
async def test_update_coin_score(db_session: AsyncSession):
    """Test updating a coin's score."""
    coin_id = uuid.uuid4()
    metrics = {
        "market_cap": {"normalized": 0.9},
        "volume_24h": {"normalized": 0.8},
    }

    score = await update_coin_score(db_session, coin_id, metrics)
    assert score.total_score is not None

    # Verify score was stored in the database
    stored_score = await get_score_by_coin(db_session, coin_id)
    assert stored_score is not None
    assert stored_score.total_score == score.total_score
