from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserResponse


class FamilySpaceBase(BaseModel):
    name: str
    family_size: int
    priorities: Optional[str] = None


class FamilySpaceCreate(FamilySpaceBase):
    pass


class FamilyMemberBase(BaseModel):
    user_id: int
    role: str  # "parent" | "child"


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberResponse(BaseModel):
    id: int
    user_id: int
    space_id: int
    role: str
    joined_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class FamilySpaceResponse(FamilySpaceBase):
    id: int
    created_at: datetime
    members: List[FamilyMemberResponse] = []

    class Config:
        from_attributes = True
