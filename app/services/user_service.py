from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


from app.core.security import hash_password


def create_user(db: Session, user: UserCreate):

    db_user = User(
        firstname=user.firstname,
        surname=user.surname,
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password) if user.password else None
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(db: Session):

    return db.query(User).all()