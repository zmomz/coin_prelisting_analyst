from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Async SQLAlchemy Engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync SQLAlchemy Engine
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),  # fallback
    echo=True,
    future=True,
)

# Sync session factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Dependency for FastAPI routes (Async)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a SQLAlchemy async session (FastAPI dependency)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
