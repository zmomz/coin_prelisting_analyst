from datetime import datetime
from uuid import UUID

from pydantic import Field as field

from app.schemas import SchemaBase


class ScoringWeightBase(SchemaBase):
    liquidity_score: float = field(ge=0.0, le=1.0)
    developer_score: float = field(ge=0.0, le=1.0)
    community_score: float = field(ge=0.0, le=1.0)
    market_score: float = field(ge=0.0, le=1.0)


class ScoringWeightCreate(ScoringWeightBase):
    pass


class ScoringWeightUpdate(ScoringWeightBase):
    pass


class ScoringWeightOut(ScoringWeightBase):
    id: UUID
    created_at: datetime
