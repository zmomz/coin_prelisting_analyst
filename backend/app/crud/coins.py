import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.coin import Coin
from app.schemas.coin import CoinCreate, CoinUpdate


async def create_coin(db: AsyncSession, coin_in: CoinCreate) -> Coin:
    coin = Coin(**coin_in.dict())
    db.add(coin)
    await db.commit()
    await db.refresh(coin)
    return coin


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
    for field, value in coin_in.dict(exclude_unset=True).items():
        setattr(db_coin, field, value)
    await db.commit()
    await db.refresh(db_coin)
    return db_coin


async def delete_coin(db: AsyncSession, db_coin: Coin):
    db_coin.is_active = False
    await db.commit()
