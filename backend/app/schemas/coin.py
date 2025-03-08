import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CoinBase(BaseModel):
    name: str
    symbol: str
    description: Optional[str] = None
    github: Optional[str] = None  


class CoinCreate(CoinBase):
    pass


class CoinUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    github: Optional[str] = None


class CoinOut(CoinBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
