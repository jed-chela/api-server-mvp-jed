from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reference = Column(String, unique=True, index=True)
    amount = Column(Float)
    plan_type = Column(String)  # "free" | "premium_monthly" | "premium_yearly"
    status = Column(String, default="active")  # "active" | "expired"
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
