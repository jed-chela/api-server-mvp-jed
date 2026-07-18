from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Budget(Base):

    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    name = Column(String, index=True)
    total_limit = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    remaining = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    expenses = relationship("Expense", back_populates="budget", cascade="all, delete-orphan")


class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), index=True)
    name = Column(String, index=True)
    amount = Column(Float, default=0.0)
    expense_date = Column(Date, index=True)
    category = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="expenses")
    creator = relationship("User")
