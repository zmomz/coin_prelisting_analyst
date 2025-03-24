from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Ensure correct async connection settings
engine = create_async_engine(
    settings.DATABASE_URL, echo=True, future=True  # ✅ Logs SQL queries to help debug
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# ✅ Fix: Ensure sessions are properly closed
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print(f"🚨 Database Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
