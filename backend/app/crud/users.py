from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user in the database."""
    hashed_password = get_password_hash(user_in.password)

    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        name=user_in.name,
        role=user_in.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: str | int) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.email == email, User.is_active == True)
    )
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User).where(User.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    updates = user_in.model_dump(exclude_unset=True)
    if "password" in updates:
        updates["hashed_password"] = get_password_hash(updates.pop("password"))

    for field, value in updates.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, db_user: User) -> None:
    db_user.is_active = False
    await db.commit()
