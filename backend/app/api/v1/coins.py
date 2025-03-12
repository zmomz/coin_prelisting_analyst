"""API endpoints for managing cryptocurrency coin listings."""

import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_manager
from app.crud.coins import create_coin, delete_coin, get_coin, get_coins, update_coin
from app.db.session import get_db
from app.models.user import User
from app.schemas.coin import CoinCreate, CoinOut, CoinUpdate

router = APIRouter(prefix="/coins", tags=["Coins"])


@router.post("/", response_model=CoinOut, status_code=status.HTTP_201_CREATED)
async def create_coin_endpoint(
    coin_in: CoinCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(get_current_manager)]
):
    """Only Managers can create new coins."""
    return await create_coin(db, coin_in)


@router.get("/{coin_id}", response_model=CoinOut)
async def get_coin_endpoint(
    coin_id: uuid.UUID, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Retrieve a coin by ID."""
    coin = await get_coin(db, coin_id)
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Coin not found"
        )
    return coin


@router.get("/", response_model=List[CoinOut])
async def get_coins_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)], 
    skip: int = 0, 
    limit: int = 100
):
    """List all coins with pagination."""
    return await get_coins(db, skip, limit)


@router.put("/{coin_id}", response_model=CoinOut)
async def update_coin_endpoint(
    coin_id: uuid.UUID, 
    coin_in: CoinUpdate, 
    _: Annotated[User, Depends(get_current_manager)],  # ✅ Enforce Manager role first
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Only Managers can update a coin."""
    coin = await get_coin(db, coin_id)
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Coin not found"
        )
    
    return await update_coin(db, coin, coin_in)


@router.delete("/{coin_id}", status_code=status.HTTP_200_OK)
async def delete_coin_endpoint(
    coin_id: uuid.UUID, 
    _: Annotated[User, Depends(get_current_manager)],  # ✅ Enforce Manager role first
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Only Managers can soft delete a coin."""
    coin = await get_coin(db, coin_id)
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Coin not found"
        )

    await delete_coin(db, coin)
    return {"message": "Coin deleted successfully"}
