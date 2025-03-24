import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.suggestion import SuggestionStatus


class SuggestionBase(BaseModel):
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)
