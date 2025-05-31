from sqlalchemy import select
from app.core.security import BearerToken
from app.database.models import User
from app.core.config import get_settings
from app.repositories.user_repository import user_repo

from typing import Annotated

from fastapi import Depends, HTTPException, Query, Request, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.pagination_schema import PaginationParams

async def async_get_db(request: Request):
    async with AsyncSession(request.app.state.db_pool) as db:
        yield db


async def get_current_user(token: BearerToken, db: Annotated[AsyncSession, Depends(async_get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, get_settings().jwt_secret_key)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await user_repo.get_by_attribute(db, attribute="id", value=int(user_id))
    if user is None:
        raise credentials_exception
    return user



# Usable Dependencies

AsyncSessionDep = Annotated[AsyncSession, Depends(async_get_db)]

PaginationParamsDep = Annotated[PaginationParams, Query()]

CurrentUserDep = Annotated[User, Depends(get_current_user)]