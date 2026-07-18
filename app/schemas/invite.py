from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InviteCreate(BaseModel):

    type: str  # "email" or "username"
    value: str  # the email or username
    role: str = "member"


class InviteResponse(BaseModel):

    id: int
    space_id: int
    invite_type: str
    invite_value: str
    role: str
    status: str
    invited_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
