from uuid import UUID
from datetime import datetime
from typing import Optional

from app.schemas import SchemaBase


class MetricCreate(SchemaBase):
    coin_id: UUID
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    github_activity: Optional[float] = None
    twitter_sentiment: Optional[float] = None
    reddit_sentiment: Optional[float] = None
    fetched_at: datetime


class MetricUpdate(SchemaBase):
    github_activity: Optional[float] = None
    twitter_sentiment: Optional[float] = None
    reddit_sentiment: Optional[float] = None


class MetricOut(SchemaBase):
    id: UUID
    coin_id: UUID
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    liquidity: Optional[float] = None
    github_activity: Optional[float] = None
    twitter_sentiment: Optional[float] = None
    reddit_sentiment: Optional[float] = None
    fetched_at: datetime
    is_active: bool
    created_at: datetime
