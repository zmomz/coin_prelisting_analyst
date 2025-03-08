from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.beat_schedule = {
    "fetch_coin_data": {
        "task": "fetch_coin_data",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    "recalculate_scores": {
        "task": "recalculate_scores",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    "notify_pending_suggestions": {
        "task": "notify_pending_suggestions",
        "schedule": 60 * 60 * 24,  # every day
    },
}

celery_app.conf.timezone = "UTC"
