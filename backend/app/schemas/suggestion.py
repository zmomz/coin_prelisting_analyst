import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.suggestion import SuggestionStatus


class SuggestionBase(BaseModel):
    note: Optional[str] = None


class SuggestionCreate(SuggestionBase):
    coin_id: uuid.UUID


class SuggestionUpdate(BaseModel):
    note: Optional[str] = None
    status: Optional[SuggestionStatus] = None


class SuggestionOut(SuggestionBase):
    id: uuid.UUID
    coin_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    status: SuggestionStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
