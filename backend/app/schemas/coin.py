import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field as field
from app.schemas import SchemaBase


class CoinBase(SchemaBase):
    name: str
    symbol: str
    coingeckoid: str
    description: Optional[str] = field(default=None)
    github: Optional[str] = field(default=None)
    x: Optional[str] = field(default=None)
    reddit: Optional[str] = field(default=None)
    telegram: Optional[str] = field(default=None)
    website: Optional[str] = field(default=None)


class CoinCreate(CoinBase):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    is_active: bool = field(default=True)


class CoinUpdate(SchemaBase):
    name: Optional[str] = field(default=None)
    symbol: Optional[str] = field(default=None)
    coingeckoid: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    github: Optional[str] = field(default=None)
    x: Optional[str] = field(default=None)
    reddit: Optional[str] = field(default=None)
    telegram: Optional[str] = field(default=None)
    website: Optional[str] = field(default=None)
    is_active: Optional[bool] = field(default=None)


class CoinOut(CoinBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
