import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.scoring import calculate_coin_score, update_coin_score
from app.crud.scores import get_score_by_coin
from app.schemas.score import ScoreMetrics


@pytest.mark.asyncio(loop_scope="session")
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


@pytest.mark.asyncio(loop_scope="session")
async def test_update_coin_score(
    db_session: AsyncSession, test_coin, scoring_weight
):
    """Test updating a coin's score with a valid scoring weight."""
    metrics = ScoreMetrics(
        market_cap=0.9,  # ✅ Pass float
        volume_24h=0.8,  # ✅ Pass float
        github_activity=0.7,  # ✅ Required field
        twitter_sentiment=0.6,  # ✅ Required field
        reddit_sentiment=0.5,  # ✅ Required field
    )

    score = await update_coin_score(
        db_session, test_coin.id, metrics, scoring_weight.id  # ✅ Use scoring_weight fixture
    )
    
    assert score.total_score is not None
    assert score.scoring_weight_id == scoring_weight.id  # ✅ Verify it's linked correctly

    # Verify score was stored in the database
    stored_score = await get_score_by_coin(db_session, test_coin.id)
    assert stored_score is not None
    assert stored_score.total_score == score.total_score
