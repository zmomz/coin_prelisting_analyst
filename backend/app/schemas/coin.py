import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CoinBase(BaseModel):
    name: str
    symbol: str
    coingeckoid: str
    description: Optional[str] = None
    github: Optional[str] = None
    x: Optional[str] = None
    reddit: Optional[str] = None
    telegram: Optional[str] = None
    website: Optional[str] = None


class CoinCreate(CoinBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class CoinUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    coingeckoid: Optional[str] = None
    description: Optional[str] = None
    github: Optional[str] = None
    x: Optional[str] = None
    reddit: Optional[str] = None
    telegram: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class CoinOut(CoinBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
