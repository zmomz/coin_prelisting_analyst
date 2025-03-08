import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.score import Score
from app.schemas.score import ScoreCreate
from app.core.config import settings
from typing import Dict, Any


async def calculate_coin_score(metrics: Dict[str, Any]) -> float:
    """Calculate a coin's score based on configurable weighting factors."""
    weights = {
        "market_cap": 0.4,
        "volume_24h": 0.2,
        "github_activity": 0.2,
        "twitter_sentiment": 0.1,
        "reddit_sentiment": 0.1,
    }

    total_score = 0.0

    for key, weight in weights.items():
        value = metrics.get(key, 0)
        if isinstance(value, dict) and "normalized" in value:
            value = value["normalized"]
        total_score += value * weight

    return round(total_score, 2)


async def update_coin_score(db: AsyncSession, coin_id: uuid.UUID, metrics: Dict[str, Any]):
    """Recalculate and store the coin's score."""
    score_value = await calculate_coin_score(metrics)

    score_entry = ScoreCreate(
        coin_id=coin_id,
        total_score=score_value,
        details=metrics,
    )

    score = Score(**score_entry.dict())
    db.add(score)
    await db.commit()
    await db.refresh(score)

    return score
