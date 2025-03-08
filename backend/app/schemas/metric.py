import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class MetricBase(BaseModel):
    market_cap: Optional[Dict[str, Any]] = None
    volume_24h: Optional[Dict[str, Any]] = None
    liquidity: Optional[Dict[str, Any]] = None

    github_activity: Optional[List[Dict[str, Any]]] = None
    twitter_sentiment: Optional[List[Dict[str, Any]]] = None
    reddit_sentiment: Optional[List[Dict[str, Any]]] = None


class MetricCreate(MetricBase):
    coin_id: uuid.UUID


class MetricUpdate(MetricBase):
    pass


class MetricOut(MetricBase):
    id: uuid.UUID
    coin_id: uuid.UUID
    is_active: bool
    fetched_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
