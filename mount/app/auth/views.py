from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.auth.models import TokenResponse, UserCreateRequest, UserRead
import app.auth.services as auth_service
from app.database.dependencies import AsyncSessionDep
from app.exceptions import HTTPExceptionResponseModel
from app.models import BaseResponseModel


auth_router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


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
    response_model=TokenResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponseModel},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponseModel},
    },
)
async def get_token(
    db: AsyncSessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_obj = await auth_service.authenticate_user(
        db=db, email=form_data.username, password=form_data.password
    )

    return {
        "access_token": user_obj.token,
        "user": user_obj
    }
