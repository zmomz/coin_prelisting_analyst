from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field as field
from app.schemas import SchemaBase


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SuggestionBase(SchemaBase):
    coin_id: UUID
    user_id: UUID
    note: Optional[str] = field(default=None)


class SuggestionCreate(SchemaBase):
    coin_id: UUID
    note: Optional[str] = field(default=None)


class SuggestionUpdate(SchemaBase):
    note: Optional[str] = field(default=None)


class SuggestionManagerUpdate(SchemaBase):
    note: Optional[str] = field(default=None)
    status: Optional[SuggestionStatus] = field(default=None)


class SuggestionOut(SuggestionBase):
    id: UUID
    status: SuggestionStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
