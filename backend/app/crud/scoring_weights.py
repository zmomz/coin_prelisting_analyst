import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.models.scoring_weight import ScoringWeight
from app.schemas.scoring_weight import ScoringWeightCreate, ScoringWeightUpdate

logger = logging.getLogger(__name__)


async def create_scoring_weight(
    db: AsyncSession, weight_in: ScoringWeightCreate
) -> ScoringWeight:
    scoring_weight = ScoringWeight(**weight_in.model_dump())
    db.add(scoring_weight)
    await db.commit()
    await db.refresh(scoring_weight)
    return scoring_weight


async def get_scoring_weight(
    db: AsyncSession, weight_id: UUID
) -> Optional[ScoringWeight]:
    result = await db.execute(
        select(ScoringWeight).where(ScoringWeight.id == weight_id)
    )
    return result.scalar_one_or_none()


async def get_scoring_weights(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[ScoringWeight]:
    result = await db.execute(
        select(ScoringWeight).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_scoring_weight(
    db: AsyncSession, db_weight: ScoringWeight, weight_in: ScoringWeightUpdate
) -> ScoringWeight:
    updates = weight_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_weight, field, value)

    await db.commit()
    await db.refresh(db_weight)
    return db_weight


async def delete_scoring_weight(
    db: AsyncSession, db_weight: ScoringWeight
) -> None:
    await db.delete(db_weight)
    await db.commit()


def getsync(db: Session, weight_id: UUID) -> ScoringWeight | None:
    return db.query(ScoringWeight).filter(ScoringWeight.id == weight_id).first()