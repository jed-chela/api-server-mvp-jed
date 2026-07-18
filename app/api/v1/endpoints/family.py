from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.family import FamilySpace, FamilyMember
from app.models.invite import FamilyInvite
from app.schemas.family import FamilySpaceResponse, FamilyMemberResponse
from app.schemas.invite import InviteCreate, InviteResponse

router = APIRouter(prefix="/family", tags=["Family"])


@router.get("/space", response_model=FamilySpaceResponse)
def get_family_space(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of any family space"
        )
    return member.space


@router.get("/members", response_model=List[FamilyMemberResponse])
def get_family_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not part of any family space"
        )

    members = db.query(FamilyMember).filter(FamilyMember.space_id == member.space_id).all()
    return members


# -------------------------
# INVITATION FLOWS
# -------------------------

@router.post("/invite", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
def invite_member(
    payload: InviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if sender belongs to a space and is a manager
    member = db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of any family space"
        )

    if member.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family space managers can invite members"
        )

    # Check if target is already in this space
    if payload.type == "username":
        target_user = db.query(User).filter(User.username == payload.value).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this username not found"
            )
        existing = db.query(FamilyMember).filter(
            FamilyMember.user_id == target_user.id,
            FamilyMember.space_id == member.space_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this family space"
            )
    elif payload.type == "email":
        target_user = db.query(User).filter(User.email == payload.value).first()
        if target_user:
            existing = db.query(FamilyMember).filter(
                FamilyMember.user_id == target_user.id,
                FamilyMember.space_id == member.space_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is already a member of this family space"
                )

    # Create the invitation
    invite = FamilyInvite(
        space_id=member.space_id,
        invite_type=payload.type,
        invite_value=payload.value,
        role=payload.role,
        status="pending",
        invited_by=current_user.id
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/invites", response_model=List[InviteResponse])
def get_my_invites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch pending invites matching current user's email or username
    conditions = [
        (FamilyInvite.invite_type == "email") & (FamilyInvite.invite_value == current_user.email)
    ]
    if current_user.username:
        conditions.append(
            (FamilyInvite.invite_type == "username") & (FamilyInvite.invite_value == current_user.username)
        )

    invites = db.query(FamilyInvite).filter(
        FamilyInvite.status == "pending",
        or_(*conditions)
    ).all()
    return invites


@router.get("/invites/pending", response_model=List[InviteResponse])
def get_pending_invites_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    # Query invites by email directly (useful for non-signed-up users)
    invites = db.query(FamilyInvite).filter(
        FamilyInvite.status == "pending",
        FamilyInvite.invite_type == "email",
        FamilyInvite.invite_value == email
    ).all()
    return invites


@router.post("/invites/{invite_id}/accept", response_model=FamilyMemberResponse)
def accept_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invite = db.query(FamilyInvite).filter(
        FamilyInvite.id == invite_id,
        FamilyInvite.status == "pending"
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending invitation not found"
        )

    # Verify if invite belongs to current user
    matches = False
    if invite.invite_type == "email" and invite.invite_value == current_user.email:
        matches = True
    elif invite.invite_type == "username" and current_user.username and invite.invite_value == current_user.username:
        matches = True

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to accept this invitation"
        )

    # Check if they are already in the space
    existing = db.query(FamilyMember).filter(
        FamilyMember.user_id == current_user.id,
        FamilyMember.space_id == invite.space_id
    ).first()

    if existing:
        invite.status = "accepted"
        db.commit()
        return existing

    # Add as new member
    new_member = FamilyMember(
        user_id=current_user.id,
        space_id=invite.space_id,
        role=invite.role
    )
    db.add(new_member)
    invite.status = "accepted"
    db.commit()
    db.refresh(new_member)
    return new_member


@router.post("/invites/{invite_id}/decline")
def decline_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    invite = db.query(FamilyInvite).filter(
        FamilyInvite.id == invite_id,
        FamilyInvite.status == "pending"
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending invitation not found"
        )

    # Verify if invite belongs to current user
    matches = False
    if invite.invite_type == "email" and invite.invite_value == current_user.email:
        matches = True
    elif invite.invite_type == "username" and current_user.username and invite.invite_value == current_user.username:
        matches = True

    if not matches:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to decline this invitation"
        )

    invite.status = "declined"
    db.commit()
    return {"message": "Invitation declined"}


# -------------------------
# MEMBER ROLE MANAGEMENT
# -------------------------

@router.put("/members/{member_id}/role", response_model=FamilyMemberResponse)
def update_member_role(
    member_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify the current user is a manager in the space
    current_member = db.query(FamilyMember).filter(FamilyMember.user_id == current_user.id).first()
    if not current_member or current_member.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only space managers can modify member roles"
        )

    # Get target member
    target_member = db.query(FamilyMember).filter(
        FamilyMember.id == member_id,
        FamilyMember.space_id == current_member.space_id
    ).first()

    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in your family space"
        )

    target_member.role = role
    db.commit()
    db.refresh(target_member)
    return target_member

