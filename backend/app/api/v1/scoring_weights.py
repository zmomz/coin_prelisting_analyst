"""API endpoints for managing scoring weight entries."""

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_manager
from app.crud.scoring_weights import (
    create_scoring_weight,
    get_scoring_weight,
    get_scoring_weights,
    update_scoring_weight,
    delete_scoring_weight,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.scoring_weight import (
    ScoringWeightCreate,
    ScoringWeightOut,
    ScoringWeightUpdate,
)

router = APIRouter(prefix="/scoring-weights", tags=["scoring_weights"])


@router.post("/", response_model=ScoringWeightOut, status_code=status.HTTP_201_CREATED)
async def create_scoring_weight_endpoint(
    weight_in: ScoringWeightCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> ScoringWeightOut:
    """Create a new scoring weight (Manager only)."""
    return await create_scoring_weight(db, weight_in)


@router.get("/{weight_id}", response_model=ScoringWeightOut)
async def get_scoring_weight_endpoint(
    weight_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ScoringWeightOut:
    """Get a specific scoring weight by ID."""
    weight = await get_scoring_weight(db, weight_id)
    if not weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scoring weight not found",
        )
    return weight


@router.get("/", response_model=List[ScoringWeightOut])
async def list_scoring_weights_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[ScoringWeightOut]:
    """List all scoring weights."""
    return await get_scoring_weights(db, skip=skip, limit=limit)


@router.put("/{weight_id}", response_model=ScoringWeightOut)
async def update_scoring_weight_endpoint(
    weight_id: uuid.UUID,
    weight_in: ScoringWeightUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> ScoringWeightOut:
    """Update a scoring weight (Manager only)."""
    db_weight = await get_scoring_weight(db, weight_id)
    if not db_weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scoring weight not found",
        )
    return await update_scoring_weight(db, db_weight, weight_in)


@router.delete("/{weight_id}", status_code=status.HTTP_200_OK)
async def delete_scoring_weight_endpoint(
    weight_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)],
) -> dict:
    """Delete a scoring weight (Manager only)."""
    db_weight = await get_scoring_weight(db, weight_id)
    if not db_weight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scoring weight not found",
        )
    await delete_scoring_weight(db, db_weight)
    return {"detail": "Scoring weight deleted successfully"}
