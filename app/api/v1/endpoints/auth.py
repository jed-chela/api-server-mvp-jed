from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.services import auth_service, otp_service

from app.database.deps import get_db, get_current_user
from app.schemas.user import UserResponse
from app.schemas.auth import (
    LoginRequest,
    SocialLoginRequest,
    SignUpRequest,
    FamilyInfoRequest,
    VerifyOTPRequest,
    ForgotPasswordRequest,
    VerifyResetOTPRequest,
    ResetPasswordRequest
)

from app.models.family import FamilySpace, FamilyMember

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()


# -------------------------
# EMAIL LOGIN
# -------------------------

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    result = auth_service.login_user(
        db,
        payload.email,
        payload.password
    )

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result


# -------------------------
# SOCIAL LOGIN
# -------------------------

@router.post("/social-login")
def social_login(payload: SocialLoginRequest, db: Session = Depends(get_db)):

    return {
        "message": "Social login",
        "provider": payload.provider
    }


# -------------------------
# SIGNUP STEP 1
# -------------------------

@router.post("/signup")
def signup(payload: SignUpRequest, db: Session = Depends(get_db)):

    user = auth_service.create_user(db, payload)

    otp_code = otp_service.create_otp(db, payload.email)

    return {
        "message": "User created. OTP sent.",
        "otp_debug": otp_code
    }


# -------------------------
# SIGNUP STEP 2
# -------------------------

@router.post("/signup/family")
def signup_family(payload: FamilyInfoRequest, db: Session = Depends(get_db)):

    # Create family space
    priorities_str = ",".join(payload.priorities) if payload.priorities else None
    family_space = FamilySpace(
        name=payload.family_space_name,
        family_size=payload.family_size,
        priorities=priorities_str
    )
    db.add(family_space)
    db.commit()
    db.refresh(family_space)

    # Link user to this space as a member
    member = FamilyMember(
        user_id=payload.user_id,
        space_id=family_space.id,
        role="manager"
    )
    db.add(member)
    db.commit()

    return {
        "message": "Family space created and member added",
        "family_space_id": family_space.id,
        "family_space_name": family_space.name
    }


# -------------------------
# VERIFY OTP
# -------------------------

@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPRequest, db: Session = Depends(get_db)):

    valid = otp_service.verify_otp(
        db,
        payload.email,
        payload.otp
    )

    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified"}


# -------------------------
# FORGOT PASSWORD STEP 1
# -------------------------

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):

    return {
        "message": "Password reset OTP sent",
        "email": payload.email
    }


# -------------------------
# VERIFY RESET OTP
# -------------------------

@router.post("/verify-reset-otp")
def verify_reset_otp(payload: VerifyResetOTPRequest):

    return {
        "message": "OTP verified"
    }


# -------------------------
# RESET PASSWORD
# -------------------------

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):

    return {
        "message": "Password updated"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(get_current_user)):

    return current_user