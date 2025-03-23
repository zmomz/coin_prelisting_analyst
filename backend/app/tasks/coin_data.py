from app.services.coin_updater import update_all_coin_metrics, update_coin_list
from app.celery_app import celery_app
import asyncio


@celery_app.task(name="app.tasks.coin_data.update_coins_list")
def update_coins_list():
    asyncio.run(update_coin_list())


@celery_app.task(name="app.tasks.coin_data.fetch_coin_data")
def fetch_coin_data():
    asyncio.run(update_all_coin_metrics())
