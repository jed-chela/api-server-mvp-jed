from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models to register them on Base.metadata
from app.models.user import User
from app.models.otp import OTP
from app.models.family import FamilySpace, FamilyMember
from app.models.event import Event
from app.models.chore import Chore
from app.models.budget import Budget, Expense
from app.models.meal import MealPlan
from app.models.photo import Album, Photo
from app.models.subscription import Subscription
from app.models.invite import FamilyInvite