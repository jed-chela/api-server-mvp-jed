from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.otp import OTP
from app.utils.otp import generate_otp


OTP_EXPIRY_MINUTES = 10


def create_otp(db: Session, email: str):

    code = generate_otp()

    expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTP(
        email = email,
        code = code,
        expires_at = expiry
    )

    db.add(otp)
    db.commit()

    return code


def verify_otp(db: Session, email: str, code: str):

    otp = (
        db.query(OTP)
        .filter(
            OTP.email == email,
            OTP.code == code,
            OTP.is_used == False
        )
        .first()
    )

    if not otp:
        return False

    if otp.expires_at < datetime.utcnow():
        return False

    otp.is_used = True
    db.commit()

    return True