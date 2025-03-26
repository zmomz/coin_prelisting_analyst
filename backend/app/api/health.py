from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter()

@router.get("/healthz", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))  # ✅ required!
        return {"status": "ok"}
    except Exception as e:
        print("🔥 DB ERROR:", repr(e))
        return {"status": "error", "message": "Database connection failed"}
