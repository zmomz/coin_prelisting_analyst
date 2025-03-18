import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CoinBase(BaseModel):
    description: Optional[str] = None
    github: Optional[str] = None
    x: Optional[str] = None
    reddit: Optional[str] = None
    telegram: Optional[str] = None
    website: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoinCreate(CoinBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # ✅ Auto-generate ID
    name: str
    symbol: str
    coingeckoid: str
    is_active: bool = True  # ✅ Default active state
    created_at: datetime = Field(default_factory=datetime.now)  # ✅ Default timestamp


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

