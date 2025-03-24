from sqlalchemy import JSON, Column, String

from app.db.base import Base


class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)
