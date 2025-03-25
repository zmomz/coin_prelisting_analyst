from typing import Optional
from sqlalchemy.orm import Session
from app.crud.metrics import create_metric_sync
from app.crud.coins import update_coin_sync, get_by_coingeckoid_sync, create_coin_sync
from app.schemas.coin import CoinCreate, CoinUpdate
from app.schemas.metric import MetricCreate
from app.models.coin import Coin
from app.utils.api_clients.coingeckosync import SyncCoinGeckoClient
from loguru import logger
from datetime import datetime


def extract_first_link(links: list) -> Optional[str]:
    return links[0] if links and isinstance(links, list) else None


def update_coin_and_metrics_from_coingecko_sync(
    db: Session,
    coin_id: str,
    coingecko_client: Optional[SyncCoinGeckoClient] = None,
) -> Optional[Coin]:
    logger.info(f"Fetching data from CoinGecko for coin: {coin_id}")
    close_client = False
    if coingecko_client is None:
        coingecko_client = SyncCoinGeckoClient()
        close_client = True

    data = coingecko_client.get_coin_data(coin_id)
    if close_client:
        coingecko_client.close()

    if not data or "id" not in data:
        logger.warning(f"No valid data returned for coin ID: {coin_id}")
        return None

    try:
        # --- COIN DATA ---
        links = data.get("links", {})
        coin_data = {
            "coingeckoid": data["id"],
            "symbol": data.get("symbol", "").upper(),
            "name": data.get("name", ""),
            "description": data.get("description", {}).get("en", "") or "",
            "github": extract_first_link(links.get("repos_url", {}).get("github", [])),
            "x": links.get("twitter_screen_name"),
            "reddit": links.get("subreddit_url"),
            "telegram": links.get("telegram_channel_identifier"),
            "website": extract_first_link(links.get("homepage", [])),
        }

        # Clean out empty fields
        coin_data = {k: (v if v not in ["", [], None] else None) for k, v in coin_data.items()}

        db_coin = get_by_coingeckoid_sync(db, coin_data["coingeckoid"])
        if db_coin:
            db_coin = update_coin_sync(db=db, db_coin=db_coin, coin_in=CoinUpdate(**coin_data))
        else:
            db_coin = create_coin_sync(db=db, coin_in=CoinCreate(**coin_data))

        # --- METRIC DATA ---
        market_data = data.get("market_data", {})
        community_data = data.get("community_data", {})
        developer_data = data.get("developer_data", {})

        metric_data = MetricCreate(
            coin_id=db_coin.id,
            market_cap=market_data.get("market_cap", {}).get("usd"),
            volume_24h=market_data.get("total_volume", {}).get("usd"),
            liquidity=market_data.get("liquidity_score"),
            github_activity=developer_data.get("commit_count_4_weeks"),
            twitter_sentiment=community_data.get("twitter_followers"),
            reddit_sentiment=community_data.get("reddit_average_posts_48h"),
            fetched_at=datetime.now(),
        )

        create_metric_sync(db, metric_in=metric_data)

        logger.success(f"✅ Updated coin and metrics: {db_coin.name}")
        return db_coin

    except Exception as e:
        logger.exception(f"❌ Exception while updating coin+metrics for '{coin_id}': {e}")
        return None
