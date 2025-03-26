import math
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.crud.metrics import create_metric_sync
from app.crud.coins import update_coin_sync, get_by_coingeckoid_sync, create_coin_sync
from app.schemas.coin import CoinCreate, CoinUpdate
from app.schemas.metric import MetricCreate
from app.models.coin import Coin
from app.utils.api_clients.coingeckosync import SyncCoinGeckoClient


def safe_extract(data: dict, *keys, default=None):
    """Safely extract nested dictionary values."""
    try:
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data
    except Exception:
        return default


def calculate_market_cap(data: dict) -> float:
    """Multiple strategies to calculate market cap."""
    try:
        # Primary method: Direct market cap
        market_cap = safe_extract(data, 'market_data', 'market_cap', 'usd')
        if market_cap and market_cap > 0:
            return market_cap

        # Fallback: Price * Circulating Supply
        price = safe_extract(data, 'market_data', 'current_price', 'usd', default=0)
        circulating_supply = safe_extract(data, 'market_data', 'circulating_supply', default=0)
        if price > 0 and circulating_supply > 0:
            return price * circulating_supply

        # Last resort: Estimated calculation
        total_volume = safe_extract(data, 'market_data', 'total_volume', 'usd', default=0)
        if total_volume > 0:
            return total_volume * 5  # Rough estimate

        return 0.01
    except Exception:
        return 0.01


def calculate_volume(data: dict) -> float:
    """Multiple strategies to calculate trading volume."""
    try:
        # Primary method: Direct 24h volume
        volume = safe_extract(data, 'market_data', 'total_volume', 'usd')
        if volume and volume > 0:
            return volume

        # Fallback: Sum of exchange volumes
        exchanges = safe_extract(data, 'tickers')
        if exchanges:
            exchange_volumes = [
                ticker.get('volume', 0) for ticker in exchanges 
                if ticker.get('converted_volume', {}).get('usd', 0) > 0
            ]
            total_exchange_volume = sum(exchange_volumes)
            if total_exchange_volume > 0:
                return total_exchange_volume

        return 0.01
    except Exception:
        return 0.01


def calculate_liquidity(market_cap: float, volume: float) -> float:
    """Advanced liquidity calculation with multiple fallback strategies."""
    try:
        if market_cap <= 0:
            return 0.01

        # Volume to Market Cap Ratio
        liquidity_score = min((volume / market_cap) * 100, 100)
        
        # Additional liquidity indicators
        return max(liquidity_score, 0.01)
    except Exception:
        return 0.01


def calculate_github_activity(data: dict) -> float:
    """Comprehensive GitHub activity calculation with multiple metrics."""
    try:
        developer_data = safe_extract(data, 'developer_data', default={})
        
        # Multiple GitHub metrics
        metrics = [
            developer_data.get('commit_count_4_weeks', 0),
            developer_data.get('forks', 0) * 2,
            developer_data.get('stars', 0),
            developer_data.get('pull_requests_merged', 0) * 3,
            len(developer_data.get('last_4_weeks_commit_activity_series', [])),
            developer_data.get('total_issues', 0),
            developer_data.get('pull_request_contributors', 0)
        ]

        # Weighted calculation with logarithmic scaling
        activity_score = sum(metrics)
        normalized_score = min(math.log(activity_score + 1) * 10, 100)
        
        return max(normalized_score, 0.01)
    except Exception:
        return 0.01


def calculate_social_sentiment(data: dict) -> tuple:
    """Advanced social sentiment calculation."""
    try:
        community_data = safe_extract(data, 'community_data', default={})
        
        # Twitter sentiment
        twitter_followers = community_data.get('twitter_followers', 0)
        twitter_score = min(math.log(twitter_followers + 1) * 5, 100)
        
        # Reddit sentiment
        reddit_metrics = [
            community_data.get('reddit_subscribers', 0),
            community_data.get('reddit_average_posts_48h', 0),
            community_data.get('reddit_accounts_active_48h', 0),
            community_data.get('reddit_average_comments_48h', 0)
        ]
        reddit_score = min(math.sqrt(sum(reddit_metrics)) / 10, 100)
        
        return (
            max(twitter_score, 0.01),
            max(reddit_score, 0.01)
        )
    except Exception:
        return (0.01, 0.01)


def extract_description(data: dict) -> str:
    """Multiple strategies to extract description."""
    try:
        # Primary: English description
        description = safe_extract(data, 'description', 'en')
        
        # Fallbacks
        if not description:
            description = safe_extract(data, 'public_notice')
        
        if not description:
            description = safe_extract(data, 'whitepaper')
        
        # Trim and truncate
        return (description or "")[:1000].strip()
    except Exception:
        return ""


def extract_link(data: dict, link_types: list) -> Optional[str]:
    """Extract first valid link from multiple sources."""
    try:
        for link_type in link_types:
            links = safe_extract(data, *link_type)
            
            # Validate and return first non-empty link
            if links and isinstance(links, list):
                valid_links = [
                    link for link in links 
                    if link and isinstance(link, str) and 
                    (link.startswith('http') or link.startswith('https'))
                ]
                if valid_links:
                    return valid_links[0]
            
            # If the link is a string, return it directly
            if isinstance(links, str) and links.startswith(('http', 'https')):
                return links
            
        return None
    except Exception:
        return None


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
        # Enhanced Coin Data Extraction
        coin_data = {
            "coingeckoid": data["id"],
            "symbol": (safe_extract(data, 'symbol', default='') or "").upper().strip(),
            "name": (safe_extract(data, 'name', default='') or "").strip(),
            "description": extract_description(data),
            "github": extract_link(data, [
                ['links', 'repos_url', 'github'],
                ['links', 'repos_url']
            ]),
            # Now that safe_extract properly drills down,
            # these fields will return a string if available
            "x": safe_extract(data, 'links', 'twitter_screen_name', default=""),
            "reddit": extract_link(data, [
                ['links', 'subreddit_url'],
                ['community_data', 'subreddit_url']
            ]),
            "telegram": safe_extract(data, 'links', 'telegram_channel_identifier', default=""),
            "website": extract_link(data, [
                ['links', 'homepage'],
                ['links']
            ]),
        }

        # Clean out empty fields
        coin_data = {k: v for k, v in coin_data.items() if v not in ["", [], None]}

        db_coin = get_by_coingeckoid_sync(db, coin_data["coingeckoid"])
        if db_coin:
            db_coin = update_coin_sync(db=db, db_coin=db_coin, coin_in=CoinUpdate(**coin_data))
        else:
            db_coin = create_coin_sync(db=db, coin_in=CoinCreate(**coin_data))

        # Enhanced Metric Calculation
        market_cap = calculate_market_cap(data)
        volume_24h = calculate_volume(data)
        liquidity = calculate_liquidity(market_cap, volume_24h)
        github_activity = calculate_github_activity(data)
        twitter_sentiment, reddit_sentiment = calculate_social_sentiment(data)

        metric_data = MetricCreate(
            coin_id=db_coin.id,
            market_cap=market_cap,
            volume_24h=volume_24h,
            liquidity=liquidity,
            github_activity=github_activity,
            twitter_sentiment=twitter_sentiment,
            reddit_sentiment=reddit_sentiment,
            fetched_at=datetime.utcnow(),
            is_active=True
        )

        create_metric_sync(db, metric_in=metric_data)

        logger.success(f"✅ Updated coin and metrics: {db_coin.name}")
        return db_coin

    except Exception as e:
        logger.exception(f"❌ Exception while updating coin+metrics for '{coin_id}': {e}")
        return None
