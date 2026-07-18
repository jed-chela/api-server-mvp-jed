from pydantic import BaseModel
from datetime import date as date_type, datetime
from typing import Optional
from app.schemas.user import UserResponse


class ChoreBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[date_type] = None
    due_time: Optional[str] = None  # e.g., "18:00"
    status: str = "open"  # "open" | "closed"
    points_reward: int = 0


class ChoreCreate(ChoreBase):
    pass


class ChoreUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[date_type] = None
    due_time: Optional[str] = None
    status: Optional[str] = None
    points_reward: Optional[int] = None


class ChoreResponse(ChoreBase):
    id: int
    space_id: int
    created_at: datetime
    assignee: Optional[UserResponse] = None

    class Config:
        from_attributes = True
