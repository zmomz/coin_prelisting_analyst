import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Text, func
    )
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class SuggestionStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    coin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
    )

    note = Column(Text, nullable=True)
    status = Column(
        Enum(SuggestionStatus, name="suggestionstatus"),
        default=SuggestionStatus.PENDING,
        nullable=False,
    )

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.timezone("UTC", func.current_timestamp()),
        onupdate=func.timezone("UTC", func.current_timestamp()),
    )
