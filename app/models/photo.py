from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Album(Base):

    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("family_spaces.id", ondelete="CASCADE"), index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    space = relationship("FamilySpace")
    creator = relationship("User")
    photos = relationship("Photo", back_populates="album", cascade="all, delete-orphan")


class Photo(Base):

    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="CASCADE"), index=True)
    file_path = Column(String)  # local storage path or Firebase URL
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    album = relationship("Album", back_populates="photos")
    uploader = relationship("User")
