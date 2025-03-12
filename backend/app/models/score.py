from sqlalchemy import Column, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Score(Base):
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    scoring_weight_id = Column(UUID(as_uuid=True), ForeignKey("scoring_weights.id", ondelete="CASCADE"), nullable=False)

    # 📌 Scoring components
    liquidity_score = Column(Float, nullable=False)
    developer_score = Column(Float, nullable=False)
    community_score = Column(Float, nullable=False)
    market_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)

    # Relationships
    coin = relationship("Coin", back_populates="scores")
    scoring_weight = relationship("ScoringWeight", back_populates="scores")  # ✅ Fixed reference

    created_at = Column(DateTime, default=datetime.now())
