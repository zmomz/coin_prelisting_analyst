import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models.suggestion import Suggestion, SuggestionStatus
from app.schemas.suggestion import SuggestionCreate, SuggestionUpdate


async def create_suggestion(
    db: AsyncSession, suggestion_in: SuggestionCreate, user_id: uuid.UUID
) -> Suggestion:
    suggestion = Suggestion(**suggestion_in.model_dump(), user_id=user_id)
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    return suggestion


async def get_suggestion(db: AsyncSession, suggestion_id: uuid.UUID) -> Optional[Suggestion]:
    result = await db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id, Suggestion.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_suggestions(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Suggestion]:
    result = await db.execute(
        select(Suggestion)
        .where(Suggestion.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_suggestion(
    db: AsyncSession, db_suggestion: Suggestion, suggestion_in: SuggestionUpdate
) -> Suggestion:
    for field, value in suggestion_in.model_dump(exclude_unset=True).items():
        setattr(db_suggestion, field, value)
    await db.commit()
    await db.refresh(db_suggestion)
    return db_suggestion


async def approve_suggestion(db: AsyncSession, db_suggestion: Suggestion):
    db_suggestion.status = SuggestionStatus.APPROVED
    await db.commit()
    await db.refresh(db_suggestion)


async def reject_suggestion(db: AsyncSession, db_suggestion: Suggestion):
    db_suggestion.status = SuggestionStatus.REJECTED
    await db.commit()
    await db.refresh(db_suggestion)


async def delete_suggestion(db: AsyncSession, db_suggestion: Suggestion):
    db_suggestion.is_active = False
    await db.commit()
