from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilyMember
from app.models.chore import Chore
from app.schemas.chore import ChoreCreate, ChoreUpdate, ChoreResponse

router = APIRouter(prefix="/chores", tags=["Chores"])


def get_user_space_id(db: Session, user_id: int) -> int:
    member = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )
    return member.space_id


@router.get("/", response_model=List[ChoreResponse])
def get_chores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    chores = db.query(Chore).filter(Chore.space_id == space_id).all()
    return chores


@router.post("/", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
def create_chore(
    payload: ChoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)

    if payload.assignee_id:
        assignee_member = db.query(FamilyMember).filter(
            FamilyMember.user_id == payload.assignee_id,
            FamilyMember.space_id == space_id
        ).first()
        if not assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a member of your family space"
            )

    db_chore = Chore(
        space_id=space_id,
        title=payload.title,
        description=payload.description,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
        due_time=payload.due_time,
        status=payload.status,
        points_reward=payload.points_reward
    )
    db.add(db_chore)
    db.commit()
    db.refresh(db_chore)
    return db_chore


@router.put("/{id}", response_model=ChoreResponse)
def update_chore(
    id: int,
    payload: ChoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_chore = db.query(Chore).filter(Chore.id == id, Chore.space_id == space_id).first()
    if not db_chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found"
        )

    for field, value in payload.dict(exclude_unset=True).items():
        if field == "assignee_id" and value:
            assignee_member = db.query(FamilyMember).filter(
                FamilyMember.user_id == value,
                FamilyMember.space_id == space_id
            ).first()
            if not assignee_member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee is not a member of your family space"
                )
        setattr(db_chore, field, value)

    db.commit()
    db.refresh(db_chore)
    return db_chore


@router.patch("/{id}/toggle", response_model=ChoreResponse)
def toggle_chore_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_chore = db.query(Chore).filter(Chore.id == id, Chore.space_id == space_id).first()
    if not db_chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found"
        )

    db_chore.status = "closed" if db_chore.status == "open" else "open"
    db.commit()
    db.refresh(db_chore)
    return db_chore


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chore(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_chore = db.query(Chore).filter(Chore.id == id, Chore.space_id == space_id).first()
    if not db_chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chore not found"
        )

    db.delete(db_chore)
    db.commit()
    return None
