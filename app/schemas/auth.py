from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional


# -------------------------
# EMAIL LOGIN
# -------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# SOCIAL LOGIN
# -------------------------

class SocialLoginRequest(BaseModel):
    provider: str  # google | apple | facebook
    token: str


# -------------------------
# SIGNUP STEP 1
# -------------------------

class SignUpRequest(BaseModel):

    fullname: Optional[str] = None
    surname: Optional[str] = None
    firstname: Optional[str] = None
    othername: Optional[str] = None
    username: Optional[str] = None

    email: EmailStr

    country_code: str
    phone_number: str

    preferred_language: str

    date_of_birth: date

    password: Optional[str] = None



# -------------------------
# FAMILY INFO
# -------------------------

class FamilyInfoRequest(BaseModel):

    user_id: int

    family_size: int

    role_in_family: str

    family_space_name: str

    priorities: List[str]


# -------------------------
# OTP VERIFY
# -------------------------

class VerifyOTPRequest(BaseModel):

    email: EmailStr
    otp: str


# -------------------------
# FORGOT PASSWORD
# -------------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str