import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class UserRole(PyEnum):
    ANALYST = "analyst"
    MANAGER = "manager"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4,
                index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(
        Enum(UserRole, name="userrole"),
        default=UserRole.ANALYST,
        nullable=False
        )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.current_timestamp()),
        nullable=False
        )
