import uuid
from sqlalchemy import Column, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    coin_id = Column(UUID(as_uuid=True), ForeignKey("coins.id", ondelete="CASCADE"), nullable=False)
    
    market_cap = Column(JSON, nullable=True)
    volume_24h = Column(JSON, nullable=True)
    liquidity = Column(JSON, nullable=True)
    
    github_activity = Column(JSON, nullable=True)
    twitter_sentiment = Column(JSON, nullable=True)
    reddit_sentiment = Column(JSON, nullable=True)

    fetched_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
