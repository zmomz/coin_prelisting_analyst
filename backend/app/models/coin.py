import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Coin(Base):
    __tablename__ = "coins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    coingeckoid = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    github = Column(String, nullable=True)
    x = Column(String, nullable=True)
    reddit = Column(String, nullable=True)
    telegram = Column(String, nullable=True)
    website = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    # Relationships
    scores = relationship("Score", back_populates="coin", cascade="all, delete-orphan")
