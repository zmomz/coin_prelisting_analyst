import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.score import Score
from app.schemas.score import ScoreIn, ScoreMetrics
from typing import Dict
from pydantic import BaseModel


class ScoreWeights(BaseModel):
    market_cap: float = 0.4
    volume_24h: float = 0.2
    github_activity: float = 0.2
    twitter_sentiment: float = 0.1
    reddit_sentiment: float = 0.1


async def calculate_coin_score(metrics: ScoreMetrics) -> float:
    """Calculate a coin's score based on configurable weighting factors."""
    weights = ScoreWeights()

    total_score = sum(
        getattr(metrics, key, 0) * getattr(weights, key, 0)
        for key in weights.model_dump()
    )

    return round(total_score, 2)


async def update_coin_score(db: AsyncSession, coin_id: uuid.UUID, metrics: ScoreMetrics) -> Score:
    """Recalculate and store the coin's score."""
    score_value = await calculate_coin_score(metrics)

    score_entry = ScoreIn(
        coin_id=coin_id,
        total_score=score_value,
        details=metrics.model_dump(),
    )

    score = Score(**score_entry.model_dump())
    db.add(score)
    await db.commit()
    await db.refresh(score)

    return score
