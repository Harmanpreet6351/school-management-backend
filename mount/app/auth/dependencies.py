



from app import logger
from app.auth.models import User
from app.config import get_settings
from app.database.dependencies import async_get_db
from app.database.operations import QueryExecutor
from .views import oauth2_scheme

from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_settings().jwt_secret_key)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = QueryExecutor(
        User,
        filter_spec=[
            ("id", "eq", int(user_id))
        ]
    ).get_one(db)
    if user is None:
        raise credentials_exception
    return user