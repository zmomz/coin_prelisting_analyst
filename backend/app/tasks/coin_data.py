import time
from loguru import logger
from app.db.session import SessionLocal
from app.services.coin_updater_sync import update_coin_and_metrics_from_coingecko_sync
from app.utils.api_clients.coingeckosync import SyncCoinGeckoClient
from app.celery_app import celery_app
from app.crud.coins import get_tracked_coins_sync


@celery_app.task(name="app.tasks.coin_data.fetch_and_update_all_coins")
def fetch_and_update_all_coins():
    """
    Sync version of Celery task to fetch & update all tracked coins and their metrics from CoinGecko.
    Updates are done sequentially with sleep to avoid rate limits.
    """
    logger.info("🚀 Starting unified coin + metrics update task from CoinGecko...")

    db = SessionLocal()
    client = SyncCoinGeckoClient()

    try:
        coin_ids = get_tracked_coins_sync(db)
        logger.debug(f"Tracked coin IDs fetched: {coin_ids}")
        if not coin_ids:
            logger.warning("⚠️ No tracked coins found to update.")
            return

        for coin_id in coin_ids:
            try:
                logger.info(f"🔄 Updating coin + metrics: {coin_id}")
                result = update_coin_and_metrics_from_coingecko_sync(db, coin_id, coingecko_client=client)
                if result:
                    logger.success(f"✅ Updated: {result.name}")
                else:
                    logger.warning(f"❌ Failed to update: {coin_id}")
            except Exception as e:
                logger.exception(f"🔥 Error updating coin '{coin_id}': {e}")
            time.sleep(1)  # 🕒 Avoid CoinGecko rate limits

        logger.info("🎉 Coin + metrics update task completed.")

    except Exception as e:
        logger.exception(f"🚨 Failed during coin update task: {e}")

    finally:
        client.close()
