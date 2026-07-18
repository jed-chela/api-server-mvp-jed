from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse


class MealPlanBase(BaseModel):
    title: str
    category: str  # Breakfast | Lunch | Dinner | Snack
    day: str  # Monday | Tuesday | etc.
    selected: bool = False
    member_id: Optional[int] = None
    notes: Optional[str] = None


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    day: Optional[str] = None
    selected: Optional[bool] = None
    member_id: Optional[int] = None
    notes: Optional[str] = None


class MealPlanResponse(MealPlanBase):
    id: int
    space_id: int
    created_at: datetime
    member: Optional[UserResponse] = None

    class Config:
        from_attributes = True
