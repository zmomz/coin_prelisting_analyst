from loguru import logger
from app.db.session import SessionLocal
from app.utils.api_clients.coingeckosync import SyncCoinGeckoClient
from app.crud.coins import create_coin_sync, get_all_coingeckoids_sync
from app.schemas.coin import CoinCreate
from app.celery_app import celery_app


@celery_app.task(name="app.tasks.bootstrap.bootstrap_supported_coins")
def bootstrap_supported_coins():
    """Sync version of the bootstrap task for Celery."""
    logger.info("📥 Bootstrapping supported coins from CoinGecko...")
    client = SyncCoinGeckoClient()

    try:
        logger.info("🔌 Fetching supported coins list from CoinGecko...")
        supported = client.get_supported_coins()
        logger.success(f"✅ Retrieved {len(supported)} supported coins from CoinGecko")

        db = SessionLocal()

        logger.info("🔎 Checking which coins already exist in the DB...")
        existing_ids = get_all_coingeckoids_sync(db)
        existing_ids_set = set(existing_ids)
        logger.info(f"📊 {len(existing_ids)} existing coins found in the database")

        new_coins = [
            coin for coin in supported
            if coin.get("id") not in existing_ids_set
        ]
        logger.info(f"📥 {len(new_coins)} new coins will be inserted")

        count = 0
        for i, coin in enumerate(new_coins, 1):
            coingeckoid = coin.get("id")
            name = coin.get("name")
            symbol = coin.get("symbol")
            if not coingeckoid or not name or not symbol:
                logger.warning(f"⚠️ Skipping coin due to missing fields: {coin}")
                continue

            try:
                create_coin_sync(db, CoinCreate(
                    coingeckoid=coingeckoid,
                    symbol=symbol.upper(),
                    name=name,
                    is_active=True,
                ))
                count += 1
                logger.debug(f"[{count}] ✅ Inserted: {name} ({symbol})")

                if count % 100 == 0:
                    logger.info(f"🔄 Progress: {count}/{len(new_coins)} coins inserted")
            except Exception as e:
                logger.warning(f"⚠️ Failed to insert coin '{coingeckoid}': {e}")

        db.commit()
        logger.success(f"🎉 Inserted {count} new coins into the database")
        logger.info("🔁 Triggering follow-up task: fetch_and_update_all_coins...")
        logger.success("✅ Bootstrapping complete.")

    except Exception as e:
        logger.exception(f"❌ Exception during bootstrap: {e}")
    finally:
        client.close()
