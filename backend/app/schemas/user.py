import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from pydantic import Field as field
from app.models.user import UserRole
from app.schemas import SchemaBase


class UserBase(SchemaBase):
    email: EmailStr
    name: Optional[str] = field(default=None)


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.ANALYST


class UserUpdate(SchemaBase):
    email: Optional[EmailStr] = field(default=None)
    name: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)
    role: Optional[UserRole] = field(default=None)


class UserOut(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
