from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.deps import get_db, get_current_user
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionVerifyRequest, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("/verify", response_model=SubscriptionResponse)
def verify_subscription(
    payload: SubscriptionVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify transaction with Paystack (Mocked/Stubbed for sandbox testing)
    # In production, execute a GET request to:
    # https://api.paystack.co/transaction/verify/{payload.reference}
    # using headers: {"Authorization": "Bearer PAYSTACK_SECRET_KEY"}

    existing = db.query(Subscription).filter(Subscription.reference == payload.reference).first()
    if existing:
        return existing

    # Create active subscription record
    db_sub = Subscription(
        user_id=current_user.id,
        reference=payload.reference,
        amount=2500.0,  # ₦2,500
        plan_type="premium_monthly",
        status="active"
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


@router.post("/webhook")
def paystack_webhook(
    event_payload: dict,
    db: Session = Depends(get_db)
):
    # In production, check X-Paystack-Signature to verify authenticity
    event_type = event_payload.get("event")

    if event_type == "charge.success":
        data = event_payload.get("data", {})
        reference = data.get("reference")
        # Handle success verification
        pass

    return {"status": "success"}
