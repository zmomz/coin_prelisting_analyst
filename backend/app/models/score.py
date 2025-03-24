import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Score(Base):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("coin_id", "scoring_weight_id", name="uix_coin_weight"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    coin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
    )
    scoring_weight_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scoring_weights.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Scoring components
    liquidity_score = Column(Float, nullable=False)
    developer_score = Column(Float, nullable=False)
    community_score = Column(Float, nullable=False)
    market_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)

    # Relationships
    coin = relationship("Coin", back_populates="scores")
    scoring_weight = relationship("ScoringWeight", back_populates="scores")

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
