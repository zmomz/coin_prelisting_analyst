from fastapi import APIRouter
from app.db.session import get_db_main
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/healthz", tags=["Health"])
async def health_check(db: AsyncSession = get_db_main()):
    """Healthcheck endpoint to verify service availability."""
    try:
        await db.execute("SELECT 1")  # Ensure DB connection is alive
        return {"status": "ok"}
    except Exception:
        return {"status": "error", "message": "Database connection failed"}
