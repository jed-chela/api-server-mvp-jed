from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class MealPlan(Base):

    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    title = Column(String, index=True)
    category = Column(String, index=True)  # e.g., "Breakfast", "Lunch", "Dinner", "Snack"
    day = Column(String, index=True)  # e.g., "Monday", "Tuesday", etc.
    selected = Column(Boolean, default=False)
    member_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    member = relationship("User")
