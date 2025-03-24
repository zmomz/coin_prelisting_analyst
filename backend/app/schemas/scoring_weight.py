from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class ScoringWeightBase(BaseModel):
    liquidity_score: float = Field(..., ge=0.0, le=1.0)
    developer_score: float = Field(..., ge=0.0, le=1.0)
    community_score: float = Field(..., ge=0.0, le=1.0)
    market_score: float = Field(..., ge=0.0, le=1.0)


# ✅ Input schema for creating a new ScoringWeight
class ScoringWeightIn(ScoringWeightBase):
    pass


# ✅ Input schema for updating an existing ScoringWeight
class ScoringWeightUpdate(ScoringWeightBase):
    pass


# ✅ Schema for database representation
class ScoringWeightInDB(ScoringWeightBase):
    id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ✅ Output schema for API responses
class ScoringWeightOut(ScoringWeightInDB):
    pass
