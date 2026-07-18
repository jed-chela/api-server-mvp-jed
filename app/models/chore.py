from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Chore(Base):

    __tablename__ = "chores"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    due_date = Column(Date, index=True, nullable=True)
    due_time = Column(String, nullable=True)  # e.g., "18:00"
    status = Column(String, default="open")  # "open" | "closed"
    points_reward = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    assignee = relationship("User")
