from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class FamilyInvite(Base):

    __tablename__ = "family_invites"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True, nullable=False)
    invite_type = Column(String, nullable=False)  # "email" or "username"
    invite_value = Column(String, nullable=False)  # the email address or username string
    role = Column(String, default="member", nullable=False)  # "member" or "manager" etc.
    status = Column(String, default="pending", nullable=False)  # "pending", "accepted", "declined"
    invited_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    inviter = relationship("User")
