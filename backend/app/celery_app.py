from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.logging import configure_logging, logger

# Configure logging early so tasks also inherit it
configure_logging()
logger.info("🔧 Initializing Celery...")

# Create Celery app
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional: autodiscover tasks from `app.tasks`
celery_app.autodiscover_tasks(["app.tasks"], force=True)

# Set timezone
celery_app.conf.timezone = "UTC"

# Celery Beat Schedule: Periodic Tasks
celery_app.conf.beat_schedule = {
    # 🪙 Fetch latest coins list from CoinGecko
    "bootstrap_supported_coins": {
        "task": "app.tasks.bootstrap.bootstrap_supported_coins",
        "schedule": crontab(hour=0, minute=0),  # Once daily at midnight UTC
    },
    # 📊 Fetch and store coin data and metrics (every 6 hours)
    "fetch_and_update_all_coins": {
        "task": "app.tasks.coin_data.fetch_and_update_all_coins",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    # 📈 Recalculate all coin scores
    "recalculate_scores": {
        "task": "app.tasks.scoring.recalculate_scores",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    # 🔔 Notify about pending suggestions
    "notify_pending_suggestions": {
        "task": "app.tasks.notifications.notify_pending_suggestions",
        "schedule": 60 * 60 * 24,  # every 24 hours
    },
}

logger.info("✅ Celery app loaded with beat schedule.")
