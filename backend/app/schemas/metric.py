from pydantic import BaseModel
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime


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
    github_activity: Dict[str, int]  # Dictionary structure for GitHub activity
    twitter_sentiment: Dict[str, float]  # Dictionary structure for Twitter sentiment
    reddit_sentiment: Dict[str, float]  # Dictionary structure for Reddit sentiment
    fetched_at: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
