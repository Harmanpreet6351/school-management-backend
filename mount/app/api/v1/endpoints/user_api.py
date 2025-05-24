from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas.user_schema import TokenRequest, TokenResponse, UserCreateRequest, UserRead
from app.services import auth_service
from app.api.dependencies import AsyncSessionDep
from app.exceptions.base_exception import HTTPExceptionResponseModel
from app.schemas.base_schema import BaseResponseModel


auth_router = APIRouter(tags=["Auth"])


@auth_router.post(
    "/auth/register",
    response_model=BaseResponseModel[UserRead],
    status_code=201
)
async def register_user(db: AsyncSessionDep, data: UserCreateRequest):
    """
    Register a new user in the system.

    This endpoint allows users to create an account by providing their
    credentials

    **Response:**
    - `200 OK`: User registered successfully.
    - `400 Bad Request`: Username already exists or invalid input.
    """
    return {
        "data": await auth_service.create_user(db, data=data)
    }


@auth_router.post(
    "/auth/token",
    response_model=BaseResponseModel[TokenResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponseModel},
    },
)
async def get_token(
    data: TokenRequest,
    db: AsyncSessionDep
):
    user_obj = await auth_service.authenticate_user(
        db=db, email=data.email, password=data.password
    )

    return {
        "data": {
            "access_token": user_obj.token,
            "user": user_obj
        }
    }
