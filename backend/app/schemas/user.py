import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.ANALYST


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserOut(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
