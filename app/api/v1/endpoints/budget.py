from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilyMember
from app.models.budget import Budget, Expense
from app.schemas.budget import BudgetCreate, BudgetResponse, ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def get_user_space_id(db: Session, user_id: int) -> int:
    member = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )
    return member.space_id


def recalculate_budget(db: Session, budget_id: int):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        return
    total_spend = sum(e.amount for e in budget.expenses)
    budget.spend = total_spend
    budget.remaining = budget.total_limit - total_spend
    db.commit()


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    budgets = db.query(Budget).filter(Budget.space_id == space_id).all()
    return budgets


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_budget = Budget(
        space_id=space_id,
        name=payload.name,
        total_limit=payload.total_limit,
        spend=0.0,
        remaining=payload.total_limit
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.put("/{id}", response_model=BudgetResponse)
def update_budget(
    id: int,
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_budget = db.query(Budget).filter(Budget.id == id, Budget.space_id == space_id).first()
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db_budget.name = payload.name
    db_budget.total_limit = payload.total_limit
    db.commit()
    recalculate_budget(db, id)
    db.refresh(db_budget)
    return db_budget


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_budget = db.query(Budget).filter(Budget.id == id, Budget.space_id == space_id).first()
    if not db_budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(db_budget)
    db.commit()
    return None


@router.get("/{budget_id}/expenses", response_model=List[ExpenseResponse])
def get_expenses(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.space_id == space_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found in family space"
        )
    return budget.expenses


@router.post("/{budget_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    budget_id: int,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.space_id == space_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found in family space"
        )

    db_expense = Expense(
        budget_id=budget_id,
        name=payload.name,
        amount=payload.amount,
        expense_date=payload.expense_date,
        category=payload.category,
        details=payload.details,
        created_by=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    recalculate_budget(db, budget_id)
    db.refresh(db_expense)
    return db_expense


@router.delete("/{budget_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    budget_id: int,
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.space_id == space_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found in family space"
        )

    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.budget_id == budget_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()
    recalculate_budget(db, budget_id)
    return None
