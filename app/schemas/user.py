from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional
from datetime import date


class UserCreate(BaseModel):

    firstname: str
    surname: str
    email: EmailStr
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):

    id: int
    firstname: str
    surname: str
    email: EmailStr
    username: Optional[str] = None
    phone_number: Optional[str] = None
    country_code: Optional[str] = None
    preferred_language: Optional[str] = None
    date_of_birth: Optional[date] = None

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.firstname} {self.surname}".strip()

    class Config:
        from_attributes = True