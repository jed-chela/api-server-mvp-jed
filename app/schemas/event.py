from pydantic import BaseModel
from datetime import date as date_type, datetime
from typing import Optional


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: date_type
    time: Optional[str] = None  # e.g. "10:30"
    category: str  # e.g. "Birthday", "Meeting", "Reminder"


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date_type] = None
    time: Optional[str] = None
    category: Optional[str] = None


class EventResponse(EventBase):
    id: int
    space_id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
