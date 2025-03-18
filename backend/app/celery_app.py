from celery import Celery
from app.core.config import settings
from celery.schedules import crontab

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.autodiscover_tasks(["app.tasks"], force=True)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "update_coins_list": {
        "task": "app.tasks.coin_data.update_coins_list",
        "schedule": crontab(hour="*/24"),  # Runs every 24 hours
    },
    "fetch_coin_data": {
        "task": "app.tasks.coin_data.fetch_coin_data",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    "recalculate_scores": {
        "task": "app.tasks.scoring.recalculate_scores",
        "schedule": 60 * 60 * 6,  # every 6 hours
    },
    "notify_pending_suggestions": {
        "task": "app.tasks.notifications.notify_pending_suggestions",
        "schedule": 60 * 60 * 24,  # every day
    },
}
