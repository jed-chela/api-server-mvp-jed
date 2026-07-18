from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Event(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    date = Column(Date, index=True)
    time = Column(String, nullable=True)  # e.g., "10:30"
    category = Column(String, index=True)  # e.g., "Birthday", "Meeting", "Reminder"
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    creator = relationship("User")
