import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.models.score import Score
from app.schemas.score import ScoreCreate


async def create_score(db: AsyncSession, score_in: ScoreCreate) -> Score:
    """Create a new score entry."""
    score = Score(**score_in.dict())
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score


async def get_score_by_coin(db: AsyncSession, coin_id: uuid.UUID) -> Optional[Score]:
    """Retrieve the latest score for a given coin."""
    result = await db.execute(
        select(Score)
        .where(Score.coin_id == coin_id, Score.is_active == True)
        .order_by(Score.calculated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
