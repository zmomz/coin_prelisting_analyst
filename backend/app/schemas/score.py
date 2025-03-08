import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ScoreBase(BaseModel):
    total_score: float
    details: Optional[Dict[str, Any]] = None  # Breakdown of score components


class ScoreCreate(ScoreBase):
    coin_id: uuid.UUID


class ScoreUpdate(BaseModel):
    total_score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class ScoreOut(ScoreBase):
    id: uuid.UUID
    coin_id: uuid.UUID
    is_active: bool
    calculated_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True
