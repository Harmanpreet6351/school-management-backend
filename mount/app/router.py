from fastapi import APIRouter
from app.auth.views import auth_router

api_router_v1 = APIRouter(prefix="/api/v1")


api_router_v1.include_router(auth_router)
