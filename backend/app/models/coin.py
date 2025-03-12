import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import relationship


class Coin(Base):
    __tablename__ = "coins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False, unique=True, index=True)
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