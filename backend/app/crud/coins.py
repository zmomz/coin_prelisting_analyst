from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

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


async def get_coin(db: AsyncSession, coin_id: str | UUID) -> Optional[Coin]:
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


async def get_tracked_coins(db: AsyncSession) -> list[str]:
    """
    Return a list of CoinGecko IDs for all coins we track.
    """
    result = await db.execute(select(Coin.coingeckoid).where(Coin.is_active == True))
    return [row[0] for row in result.fetchall() if row[0]]


async def get_by_coingeckoid(db: AsyncSession, coingeckoid: str) -> Coin | None:
    """ Special function help in exposing coins for fast updates """
    result = await db.execute(
        select(Coin).where(Coin.coingeckoid == coingeckoid, Coin.is_active == True)
    )
    return result.scalars().first()


async def get_all_coingeckoids(db: AsyncSession) -> list[str]:
    """ Special function to check all available coins """
    result = await db.execute(select(Coin.coingeckoid))
    return [row[0] for row in result.all()]


# create_coin_sync, get_all_coingeckoids_sync

def get_all_coingeckoids_sync(db: Session) -> list[str]:
    """Sync version to get all CoinGecko IDs from the database."""
    result = db.execute(select(Coin.coingeckoid))
    return [row[0] for row in result.all()]


def create_coin_sync(db: Session, coin_in: CoinCreate) -> Coin:
    """Sync version to create a new coin."""
    coin = Coin(**coin_in.model_dump())
    db.add(coin)

    try:
        db.commit()
        db.refresh(coin)
        return coin
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Coin symbol already exists"
        )


def get_by_coingeckoid_sync(db: Session, coingeckoid: str) -> Optional[Coin]:
    return db.query(Coin).filter(Coin.coingeckoid == coingeckoid).first()


def update_coin_sync(db: Session, db_coin: Coin, coin_in: CoinUpdate) -> Coin:
    for field, value in coin_in.model_dump(exclude_unset=True).items():
        setattr(db_coin, field, value)
    db.commit()
    db.refresh(db_coin)
    return db_coin


def get_tracked_coins_sync(db: Session) -> list[str]:
    result = db.execute(select(Coin.coingeckoid).where(Coin.is_active == True))
    return [row[0] for row in result.all()]
