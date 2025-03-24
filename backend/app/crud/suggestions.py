import logging
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.suggestion import Suggestion, SuggestionStatus
from app.schemas.suggestion import (
    SuggestionUpdate,
    SuggestionManagerUpdate,
)

logger = logging.getLogger(__name__)


async def create_suggestion(
    db: AsyncSession,
    coin_id: UUID,
    user_id: UUID,
    note: Optional[str],
) -> Suggestion:
    suggestion = Suggestion(
        id=uuid4(),
        coin_id=coin_id,
        user_id=user_id,
        note=note,
        status=SuggestionStatus.PENDING,
        is_active=True,
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)
    return suggestion


async def get_suggestion(
    db: AsyncSession, suggestion_id: UUID
) -> Optional[Suggestion]:
    result = await db.execute(
        select(Suggestion).where(Suggestion.id == suggestion_id, Suggestion.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_suggestions_by_coin(
    db: AsyncSession, coin_id: UUID
) -> list[Suggestion]:
    result = await db.execute(
        select(Suggestion).where(Suggestion.coin_id == coin_id, Suggestion.is_active == True)
    )
    return result.scalars().all()


async def update_suggestion_by_user(
    db: AsyncSession, db_suggestion: Suggestion, update_in: SuggestionUpdate
) -> Suggestion:
    for field, value in update_in.model_dump(exclude_unset=True).items():
        setattr(db_suggestion, field, value)
    await db.commit()
    await db.refresh(db_suggestion)
    return db_suggestion


async def update_suggestion_by_manager(
    db: AsyncSession,
    db_suggestion: Suggestion,
    update_in: SuggestionManagerUpdate
) -> Suggestion:
    for field, value in update_in.model_dump(exclude_unset=True).items():
        if field == "status" and value is not None:
            value = SuggestionStatus(value)
        setattr(db_suggestion, field, value)
    await db.commit()
    await db.refresh(db_suggestion)
    return db_suggestion


async def delete_suggestion(
    db: AsyncSession, db_suggestion: Suggestion
) -> None:
    db_suggestion.is_active = False
    await db.commit()
