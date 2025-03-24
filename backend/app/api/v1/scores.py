"""API endpoints for managing scoring entries."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_manager
from app.crud.scores import (
    create_score,
    delete_score,
    get_score,
    get_scores_by_coin,
    update_score,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.score import ScoreCreate, ScoreOut, ScoreUpdate

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("/", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
async def create_score_endpoint(
    score_in: ScoreCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> ScoreOut:
    """Create a new score (Manager only)."""
    return await create_score(db, score_in)


@router.get("/{score_id}", response_model=ScoreOut)
async def get_score_endpoint(
    score_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ScoreOut:
    """Get a score by ID."""
    score = await get_score(db, score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score


@router.get("/by-coin/{coin_id}", response_model=List[ScoreOut])
async def get_scores_by_coin_endpoint(
    coin_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ScoreOut]:
    """List all scores for a given coin."""
    return await get_scores_by_coin(db, coin_id)


@router.put("/{score_id}", response_model=ScoreOut)
async def update_score_endpoint(
    score_id: uuid.UUID,
    score_in: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> ScoreOut:
    """Update an existing score (Manager only)."""
    score = await get_score(db, score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    return await update_score(db, score, score_in)


@router.delete("/{score_id}", status_code=status.HTTP_200_OK)
async def delete_score_endpoint(
    score_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_manager),
) -> dict:
    """Delete a score entry (Manager only)."""
    score = await get_score(db, score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")

    await delete_score(db, score)
    return {"detail": "Score deleted successfully"}
