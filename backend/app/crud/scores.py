import logging
from uuid import UUID
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.score import Score
from app.schemas.score import ScoreCreate, ScoreUpdate

logger = logging.getLogger(__name__)


async def create_score(db: AsyncSession, score_in: ScoreCreate) -> Score:
    score = Score(**score_in.model_dump())
    db.add(score)
    try:
        await db.commit()
        await db.refresh(score)
        return score
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"🚨 IntegrityError creating score: {e}")
        raise HTTPException(
            status_code=409,
            detail="Score for this coin and weight already exists.",
        )


async def get_score(db: AsyncSession, score_id: UUID) -> Optional[Score]:
    result = await db.execute(select(Score).where(Score.id == score_id))
    return result.scalar_one_or_none()


async def get_scores_by_coin(
        db: AsyncSession, coin_id: UUID
) -> list[Score]:
    result = await db.execute(select(Score).where(Score.coin_id == coin_id))
    return result.scalars().all()


async def update_score(
    db: AsyncSession, db_score: Score, score_in: ScoreUpdate
) -> Score:
    for field, value in score_in.model_dump(exclude_unset=True).items():
        setattr(db_score, field, value)
    await db.commit()
    await db.refresh(db_score)
    return db_score


async def delete_score(db: AsyncSession, db_score: Score) -> None:
    await db.delete(db_score)
    await db.commit()
