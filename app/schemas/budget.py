from pydantic import BaseModel
from datetime import date as date_type, datetime
from typing import List, Optional
from app.schemas.user import UserResponse


class ExpenseBase(BaseModel):
    name: str
    amount: float
    expense_date: date_type
    category: Optional[str] = None
    details: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    budget_id: int
    created_by: Optional[int] = None
    created_at: datetime
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    name: str
    total_limit: float = 0.0


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    space_id: int
    spend: float
    remaining: float
    created_at: datetime
    expenses: List[ExpenseResponse] = []

    class Config:
        from_attributes = True
