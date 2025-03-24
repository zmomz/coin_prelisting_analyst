import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Metric(Base):
    __tablename__ = "metrics"

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
        index=True,
    )
    market_cap = Column(JSON, nullable=False)
    volume_24h = Column(JSON, nullable=False)
    liquidity = Column(JSON, nullable=False)
    github_activity = Column(JSON, nullable=True)
    twitter_sentiment = Column(JSON, nullable=True)
    reddit_sentiment = Column(JSON, nullable=True)
    fetched_at = Column(
        DateTime,
        nullable=False,
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.timezone("UTC", func.current_timestamp()),
    )
