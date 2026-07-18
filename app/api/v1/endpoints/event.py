from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilyMember
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


def get_user_space_id(db: Session, user_id: int) -> int:
    member = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )
    return member.space_id


@router.get("/", response_model=List[EventResponse])
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    events = db.query(Event).filter(Event.space_id == space_id).all()
    return events


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_event = Event(
        space_id=space_id,
        name=payload.name,
        description=payload.description,
        date=payload.date,
        time=payload.time,
        category=payload.category,
        created_by=current_user.id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.put("/{id}", response_model=EventResponse)
def update_event(
    id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_event = db.query(Event).filter(Event.id == id, Event.space_id == space_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_event, field, value)

    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    space_id = get_user_space_id(db, current_user.id)
    db_event = db.query(Event).filter(Event.id == id, Event.space_id == space_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    db.delete(db_event)
    db.commit()
    return None
