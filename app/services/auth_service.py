from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


# -------------------------
# REGISTER USER
# -------------------------

def create_user(db: Session, payload):

    firstname = payload.firstname
    surname = payload.surname

    if payload.fullname and not (firstname and surname):
        parts = payload.fullname.strip().split(" ", 1)
        firstname = parts[0]
        surname = parts[1] if len(parts) > 1 else ""

    user = User(
        email=payload.email,
        username=getattr(payload, "username", None),
        firstname=firstname or "",
        surname=surname or "",
        password_hash=hash_password(payload.password) if payload.password else None,
        phone_number=payload.phone_number,
        country_code=payload.country_code,
        preferred_language=payload.preferred_language,
        date_of_birth=payload.date_of_birth
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -------------------------
# LOGIN USER
# -------------------------

def login_user(db: Session, email: str, password: str):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    token = create_access_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }