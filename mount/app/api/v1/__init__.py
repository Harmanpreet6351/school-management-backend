from fastapi import APIRouter

from app.api.v1.endpoints.user_api import auth_router


v1_router = APIRouter(
    prefix="/v1"
)


v1_router.include_router(auth_router)