import uuid
from datetime import datetime

from pydantic import Field as field

from app.schemas import SchemaBase


class ScoreBase(SchemaBase):
    liquidity_score: float = field(..., ge=0.0, le=1.0)
    developer_score: float = field(..., ge=0.0, le=1.0)
    community_score: float = field(..., ge=0.0, le=1.0)
    market_score: float = field(..., ge=0.0, le=1.0)
    final_score: float = field(..., ge=0.0, le=1.0)


class ScoreCreate(ScoreBase):
    coin_id: uuid.UUID
    scoring_weight_id: uuid.UUID


class ScoreUpdate(ScoreBase):
    pass


class ScoreOut(ScoreBase):
    id: uuid.UUID
    coin_id: uuid.UUID
    scoring_weight_id: uuid.UUID
    created_at: datetime
