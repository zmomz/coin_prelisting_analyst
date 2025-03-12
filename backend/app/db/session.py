from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create Async Engines for Main and Test Databases
engine_main = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

engine_test = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    future=True
)

# Create Async Session factories
AsyncSessionLocalMain = sessionmaker(
    bind=engine_main,
    class_=AsyncSession,
    expire_on_commit=False
)

AsyncSessionLocalTest = sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False
)


# ✅ Async Dependency: Get Main DB Session
async def get_db_main():
    async with AsyncSessionLocalMain() as session:
        try:
            yield session
        except Exception as e:
            print(f"🚨 Database Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# ✅ Async Dependency: Get Test DB Session
async def get_db_test():
    async with AsyncSessionLocalTest() as session:
        try:
            yield session
        except Exception as e:
            print(f"🚨 Test Database Error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
