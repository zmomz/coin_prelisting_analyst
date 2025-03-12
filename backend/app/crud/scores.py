import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.models.score import Score
from app.schemas.score import ScoreIn, ScoreOut


async def create_score(db: AsyncSession, score_in: ScoreIn) -> ScoreOut:
    """Create a new score entry and return the structured response."""
    score = Score(**score_in.model_dump())

    db.add(score)
    await db.commit()
    await db.refresh(score)

    return ScoreOut.model_validate(score)


async def get_score_by_coin(db: AsyncSession, coin_id: uuid.UUID) -> Optional[ScoreOut]:
    """Retrieve the latest active score for a given coin."""
    result = await db.execute(
        select(Score)
        .where(Score.coin_id == coin_id, Score.is_active == True)
        .order_by(Score.calculated_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()

    return ScoreOut.model_validate(score) if score else None
