from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SubscriptionVerifyRequest(BaseModel):
    reference: str


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    reference: str
    amount: float
    plan_type: str
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
