import uuid
from sqlalchemy import Column, ForeignKey, Float, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)

    total_score = Column(Float, nullable=False)
    details = Column(JSON, nullable=True)  # To store breakdown of how the score was calculated

    calculated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
