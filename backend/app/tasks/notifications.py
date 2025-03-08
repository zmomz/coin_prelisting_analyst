import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.services.notifications import send_slack_notification
from app.crud.suggestions import get_suggestions
from app.models.suggestion import SuggestionStatus


@celery_app.task(name="notify_pending_suggestions")
async def notify_pending_suggestions():
    """Sends a Slack notification for pending suggestions."""
    async with AsyncSessionLocal() as db:
        suggestions = await get_suggestions(db)

        pending_suggestions = [
            s for s in suggestions if s.status == SuggestionStatus.PENDING
        ]

        if pending_suggestions:
            message = f"🔔 There are {len(pending_suggestions)} pending suggestions for review."
            await send_slack_notification(message)
