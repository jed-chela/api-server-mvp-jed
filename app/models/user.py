from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from app.database.base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)

    username = Column(String, unique=True, index=True, nullable=True)

    firstname = Column(String)

    surname = Column(String)

    password_hash = Column(String)

    country_code = Column(String, nullable=True)

    phone_number = Column(String, nullable=True)

    preferred_language = Column(String, default="en")

    date_of_birth = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)