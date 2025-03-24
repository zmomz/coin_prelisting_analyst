from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/healthz", tags=["Health"])
async def health_check(db: AsyncSession = get_db()):
    """Healthcheck endpoint to verify service availability."""
    try:
        await db.execute("SELECT 1")  # Ensure DB connection is alive
        return {"status": "ok"}
    except Exception:
        return {"status": "error", "message": "Database connection failed"}
