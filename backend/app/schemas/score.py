from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class ScoreBase(BaseModel):
    liquidity_score: float = Field(..., ge=0.0, le=1.0)
    developer_score: float = Field(..., ge=0.0, le=1.0)
    community_score: float = Field(..., ge=0.0, le=1.0)
    market_score: float = Field(..., ge=0.0, le=1.0)
    final_score: float = Field(..., ge=0.0, le=1.0)


# ✅ Input schema for creating a new Score
class ScoreIn(ScoreBase):
    coin_id: UUID4
    scoring_weight_id: UUID4


# ✅ Input schema for updating an existing Score
class ScoreUpdate(ScoreBase):
    pass


# ✅ Schema for database representation (includes ID and timestamps)
class ScoreInDB(ScoreBase):
    id: UUID4
    coin_id: UUID4
    scoring_weight_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ✅ Output schema for returning Score in API responses
class ScoreOut(ScoreInDB):
    pass


class ScoreMetrics(BaseModel):
    market_cap: float
    volume_24h: float
    github_activity: float
    twitter_sentiment: float
    reddit_sentiment: float
