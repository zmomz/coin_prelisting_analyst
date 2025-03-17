import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CoinBase(BaseModel):
    name: str
    symbol: str
    description: Optional[str] = None
    github: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoinCreate(CoinBase):
    name: str
    symbol: str
    coingeckoid: str
    description: Optional[str] = None
    github: Optional[str] = None
    id: uuid.UUID = uuid.uuid4()  # ✅ Auto-generate ID if needed
    is_active: bool = True  # ✅ Default active state
    created_at: datetime = datetime.now()  # ✅ Default timestamp


class CoinUpdate(BaseModel):
    name: Optional[str]
    symbol: Optional[str]
    description: Optional[str]
    github: Optional[str]


class CoinOut(CoinBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
