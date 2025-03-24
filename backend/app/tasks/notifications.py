import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.suggestion import Suggestion, SuggestionStatus
from app.services.notifications import send_slack_notification

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.notifications.notify_pending_suggestions")
def notify_pending_suggestions(
    session_maker: sessionmaker[Session] = AsyncSessionLocal,
):
    """Entrypoint for Celery to run the async logic."""
    asyncio.run(notify_pending_suggestions_async(session_maker))


async def notify_pending_suggestions_async(session_maker: sessionmaker[Session]):
    """Check for pending suggestions and send Slack alert if any exist."""
    async with session_maker() as db:
        # Fetch number of pending suggestions
        pending_count = await _count_pending_suggestions(db)

        if pending_count > 0:
            message = f"🔔 {pending_count} pending suggestions need review."
            logger.info("Sending Slack notification...")
            await send_slack_notification(message)
        else:
            logger.info("No pending suggestions found; Slack notification skipped.")


async def _count_pending_suggestions(db):
    """Helper that returns how many suggestions have status == PENDING."""
    stmt = select(Suggestion).where(Suggestion.status == SuggestionStatus.PENDING)
    results = await db.execute(stmt)
    pending_suggestions = results.scalars().all()
    return len(pending_suggestions)
