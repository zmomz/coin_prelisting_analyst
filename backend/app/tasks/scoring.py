import asyncio
import logging

from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.scoring import recalculate_scores_service

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scoring.recalculate_scores")
def recalculate_scores():
    """Celery-compatible wrapper for async function."""
    asyncio.run(recalculate_scores_async())


async def recalculate_scores_async():
    """Async function to recalculate scores."""
    async with AsyncSessionLocal() as db:
        logger.info("Recalculating scores...")
        result = await recalculate_scores_service(db)

        if not result["success"]:
            logger.error(f"Score recalculation failed: {result['error']}")
        else:
            logger.info(
                f"Score recalculation complete. Updated {result['updated_scores']} scores."
            )
