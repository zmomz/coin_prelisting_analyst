from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MetricValueSchema(BaseModel):
    value: float
    currency: str


class MetricCreate(BaseModel):
    """Schema for creating a new metric entry."""

    coin_id: UUID
    market_cap: MetricValueSchema
    volume_24h: MetricValueSchema
    liquidity: MetricValueSchema
    github_activity: Optional[int] = None
    twitter_sentiment: Optional[float] = None
    reddit_sentiment: Optional[float] = None
    fetched_at: datetime


class MetricResponseSchema(BaseModel):
    id: UUID
    coin_id: UUID
    market_cap: MetricValueSchema
    volume_24h: MetricValueSchema
    liquidity: MetricValueSchema
    github_activity: dict[str, int]
    twitter_sentiment: dict[str, float]
    reddit_sentiment: dict[str, float]
    fetched_at: datetime
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
