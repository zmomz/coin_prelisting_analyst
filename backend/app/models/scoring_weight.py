import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ScoringWeight(Base):
    __tablename__ = "scoring_weights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # 📌 Weights for each scoring category
    liquidity_score = Column(Float, nullable=False)
    developer_score = Column(Float, nullable=False)
    community_score = Column(Float, nullable=False)
    market_score = Column(Float, nullable=False)

    # 📌 Metadata
    created_at = Column(DateTime, default=datetime.now())

    # Relationship for backward reference
    scores = relationship("Score", back_populates="scoring_weight")
