from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilyMember
from app.models.meal import MealPlan
from app.schemas.meal import MealPlanCreate, MealPlanUpdate, MealPlanResponse

router = APIRouter(prefix="/meals", tags=["Meals"])


def get_user_space_id(db: Session, user_id: int) -> int:
    member = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )
    return member.space_id


@router.get("/", response_model=List[MealPlanResponse])
def get_meals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    meals = db.query(MealPlan).filter(MealPlan.space_id == space_id).all()
    return meals


@router.post("/", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
def create_meal(
    payload: MealPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)

    if payload.member_id:
        member = db.query(FamilyMember).filter(
            FamilyMember.user_id == payload.member_id,
            FamilyMember.space_id == space_id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned member is not part of your family space"
            )

    db_meal = MealPlan(
        space_id=space_id,
        title=payload.title,
        category=payload.category,
        day=payload.day,
        selected=payload.selected,
        member_id=payload.member_id,
        notes=payload.notes
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal


@router.put("/{id}", response_model=MealPlanResponse)
def update_meal(
    id: int,
    payload: MealPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_meal = db.query(MealPlan).filter(MealPlan.id == id, MealPlan.space_id == space_id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    for field, value in payload.dict(exclude_unset=True).items():
        if field == "member_id" and value:
            member = db.query(FamilyMember).filter(
                FamilyMember.user_id == value,
                FamilyMember.space_id == space_id
            ).first()
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assigned member is not part of your family space"
                )
        setattr(db_meal, field, value)

    db.commit()
    db.refresh(db_meal)
    return db_meal


@router.patch("/{id}/toggle", response_model=MealPlanResponse)
def toggle_meal_selection(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_meal = db.query(MealPlan).filter(MealPlan.id == id, MealPlan.space_id == space_id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    db_meal.selected = not db_meal.selected
    db.commit()
    db.refresh(db_meal)
    return db_meal


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_meal = db.query(MealPlan).filter(MealPlan.id == id, MealPlan.space_id == space_id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )

    db.delete(db_meal)
    db.commit()
    return None
