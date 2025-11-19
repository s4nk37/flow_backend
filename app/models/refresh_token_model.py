from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone

from app.database.session import Base
from app.core.security import REFRESH_TOKEN_EXPIRE_DAYS


def utcnow():
    # helper for SQLAlchemy defaults
    return datetime.now(timezone.utc)


def refresh_expiry():
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    user_agent = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=utcnow)
    expires_at = Column(DateTime(timezone=True), default=refresh_expiry)

    user = relationship("UserModel")
