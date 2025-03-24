from typing import Optional
import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.coin import Coin
from app.schemas.coin import CoinCreate, CoinUpdate


async def create_coin(db: AsyncSession, coin_in: CoinCreate) -> Coin:
    """Create a new coin."""
    coin = Coin(**coin_in.model_dump())
    db.add(coin)

    try:
        await db.commit()
        await db.refresh(coin)
        return coin
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Coin symbol already exists"
        )


async def get_coin(db: AsyncSession, coin_id: str | uuid.UUID) -> Optional[Coin]:
    """Retrieve a coin by ID."""
    result = await db.execute(
        select(Coin).where(Coin.id == coin_id, Coin.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_coin_by_symbol(db: AsyncSession, symbol: str) -> Optional[Coin]:
    """Retrieve a coin by its symbol."""
    result = await db.execute(
        select(Coin).where(Coin.symbol == symbol, Coin.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_coins(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Coin]:
    """Get a list of all active coins."""
    result = await db.execute(
        select(Coin).where(Coin.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_coin(db: AsyncSession, db_coin: Coin, coin_in: CoinUpdate) -> Coin:
    """Update a coin's fields."""
    updates = coin_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_coin, field, value)

    await db.commit()
    await db.refresh(db_coin)
    return db_coin


async def delete_coin(db: AsyncSession, db_coin: Coin) -> None:
    """Soft delete a coin."""
    db_coin.is_active = False
    await db.commit()
