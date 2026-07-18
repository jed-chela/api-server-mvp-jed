from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class FamilySpace(Base):

    __tablename__ = "family_spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    family_size = Column(Integer, default=1)
    priorities = Column(String, nullable=True)  # Store priorities as comma-separated values or JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("FamilyMember", back_populates="space", cascade="all, delete-orphan")


class FamilyMember(Base):

    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    role = Column(String, default="member")  # e.g., "parent" | "child"
    joined_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace", back_populates="members")
    user = relationship("User")
