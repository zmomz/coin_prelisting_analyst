import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud.suggestions import (
    create_suggestion,
    delete_suggestion,
    get_suggestion,
    get_suggestions_by_coin,
    update_suggestion_by_user,
    update_suggestion_by_manager,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.suggestion import (
    SuggestionCreate,
    SuggestionOut,
    SuggestionUpdate,
    SuggestionManagerUpdate,
)

router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"],
    dependencies=[Depends(get_current_user)],  # 🔒 Require authentication globally
)


@router.post("/", response_model=SuggestionOut, status_code=201)
async def create_suggestion_endpoint(
    suggestion_in: SuggestionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_suggestion(
        db=db,
        coin_id=suggestion_in.coin_id,
        user_id=current_user.id,
        note=suggestion_in.note,
    )


@router.get("/{suggestion_id}", response_model=SuggestionOut)
async def get_suggestion_endpoint(
    suggestion_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> SuggestionOut:
    """Get a suggestion by ID (authenticated users only)."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion


@router.get("/coin/{coin_id}", response_model=list[SuggestionOut])
async def get_suggestions_by_coin_endpoint(
    coin_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[SuggestionOut]:
    """Get all suggestions for a given coin (authenticated users only)."""
    return await get_suggestions_by_coin(db, coin_id)


@router.put("/{suggestion_id}", response_model=SuggestionOut)
async def update_suggestion_endpoint(
    suggestion_id: uuid.UUID,
    update_in: SuggestionUpdate | SuggestionManagerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SuggestionOut:
    """Update a suggestion (users update note, managers update note + status)."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if current_user.role == UserRole.MANAGER:
        return await update_suggestion_by_manager(db, suggestion, update_in)  # type: ignore

    if suggestion.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return await update_suggestion_by_user(db, suggestion, update_in)  # type: ignore


@router.delete("/{suggestion_id}", status_code=status.HTTP_200_OK)
async def delete_suggestion_endpoint(
    suggestion_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Soft delete a suggestion (owner or manager only)."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if current_user.role != UserRole.MANAGER and suggestion.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await delete_suggestion(db, suggestion)
    return {"detail": "Suggestion deleted successfully"}
