import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as UUIDType 
from datetime import datetime
from app.db.base import Base


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)  # Description of the action performed
    resource_type = Column(String, nullable=False)  # e.g., "coin", "suggestion"
    resource_id = Column(UUIDType(as_uuid=True), nullable=True)  # ID of the affected resource

    created_at = Column(DateTime, default=datetime.utcnow)
