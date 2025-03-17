from fastapi import HTTPException
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.models.coin import Coin
from app.schemas.coin import CoinCreate, CoinUpdate
from sqlalchemy.exc import IntegrityError
import logging
logger = logging.getLogger(__name__)


async def create_coin(db: AsyncSession, coin_in: CoinCreate) -> Coin:
    coin = Coin(**coin_in.model_dump())
    db.add(coin)
    try:
        await db.commit()
        await db.refresh(coin)
        return coin
    except IntegrityError as e:
        await db.rollback()  # ✅ Rollback the transaction on failure
        logger.error(f"🚨 Database Integrity Error: {e}")
        raise HTTPException(status_code=409, detail="Coin symbol already exists")  # ✅ Return 409 Conflict


async def get_coin(db: AsyncSession, coin_id: uuid.UUID) -> Optional[Coin]:
    result = await db.execute(
        select(Coin).where(Coin.id == coin_id, Coin.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_coin_by_symbol(db: AsyncSession, symbol: str) -> Optional[Coin]:
    result = await db.execute(
        select(Coin).where(Coin.symbol == symbol, Coin.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_coins(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[Coin]:
    result = await db.execute(
        select(Coin)
        .where(Coin.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_coin(
    db: AsyncSession, db_coin: Coin, coin_in: CoinUpdate
) -> Coin:
    for field, value in coin_in.model_dump(exclude_unset=True).items():
        setattr(db_coin, field, value)
    await db.commit()
    await db.refresh(db_coin)
    return db_coin


async def delete_coin(db: AsyncSession, db_coin: Coin):
    db_coin.is_active = False
    await db.commit()
