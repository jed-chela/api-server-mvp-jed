from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import family
from app.api.v1.endpoints import event
from app.api.v1.endpoints import chore
from app.api.v1.endpoints import budget
from app.api.v1.endpoints import meal
from app.api.v1.endpoints import photo
from app.api.v1.endpoints import subscription

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(family.router)
api_router.include_router(event.router)
api_router.include_router(chore.router)
api_router.include_router(budget.router)
api_router.include_router(meal.router)
api_router.include_router(photo.router)
api_router.include_router(subscription.router)