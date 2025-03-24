from uuid import UUID
from datetime import datetime
from typing import Optional

from app.schemas import SchemaBase


class MetricValue(SchemaBase):
    value: float
    currency: str


class MetricCreate(SchemaBase):
    coin_id: UUID
    market_cap: MetricValue
    volume_24h: MetricValue
    liquidity: MetricValue
    github_activity: Optional[dict] = None
    twitter_sentiment: Optional[dict] = None
    reddit_sentiment: Optional[dict] = None
    fetched_at: datetime


class MetricUpdate(SchemaBase):
    github_activity: Optional[dict] = None
    twitter_sentiment: Optional[dict] = None
    reddit_sentiment: Optional[dict] = None


class MetricOut(SchemaBase):
    id: UUID
    coin_id: UUID
    market_cap: dict
    volume_24h: dict
    liquidity: dict
    github_activity: Optional[dict] = None
    twitter_sentiment: Optional[dict] = None
    reddit_sentiment: Optional[dict] = None
    fetched_at: datetime
    is_active: bool
    created_at: datetime
