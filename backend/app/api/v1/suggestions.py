import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.suggestion import SuggestionStatus
from app.crud.suggestions import (
    create_suggestion, 
    get_suggestion, 
    get_suggestions, 
    update_suggestion, 
    approve_suggestion, 
    reject_suggestion, 
    delete_suggestion
)
from app.schemas.suggestion import SuggestionCreate, SuggestionUpdate, SuggestionOut
from app.api.deps import get_current_user, get_current_manager

router = APIRouter()


@router.post("/", response_model=SuggestionOut)
async def create_suggestion_endpoint(
    suggestion_in: SuggestionCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Analysts can create coin listing suggestions."""
    return await create_suggestion(db, suggestion_in, current_user.id)


@router.get("/{suggestion_id}", response_model=SuggestionOut)
async def get_suggestion_endpoint(suggestion_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific suggestion by ID."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    return suggestion


@router.get("/", response_model=List[SuggestionOut])
async def get_suggestions_endpoint(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """List all suggestions with pagination."""
    return await get_suggestions(db, skip, limit)


@router.put("/{suggestion_id}", response_model=SuggestionOut)
async def update_suggestion_endpoint(
    suggestion_id: uuid.UUID, 
    suggestion_in: SuggestionUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Analysts can update their own suggestions before approval/rejection."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    if suggestion.user_id != current_user.id and current_user.role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return await update_suggestion(db, suggestion, suggestion_in)


@router.post("/{suggestion_id}/approve")
async def approve_suggestion_endpoint(
    suggestion_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_manager)
):
    """Managers can approve suggestions."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    if suggestion.status != SuggestionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggestion is already processed")

    await approve_suggestion(db, suggestion)
    return {"detail": "Suggestion approved"}


@router.post("/{suggestion_id}/reject")
async def reject_suggestion_endpoint(
    suggestion_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_manager)
):
    """Managers can reject suggestions."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    if suggestion.status != SuggestionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Suggestion is already processed")

    await reject_suggestion(db, suggestion)
    return {"detail": "Suggestion rejected"}


@router.delete("/{suggestion_id}")
async def delete_suggestion_endpoint(
    suggestion_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_manager)
):
    """Managers can soft delete suggestions."""
    suggestion = await get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")

    await delete_suggestion(db, suggestion)
    return {"detail": "Suggestion deleted successfully"}
