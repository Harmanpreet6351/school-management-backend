from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.auth.exceptions import InvalidUsernamePasswordException, UserAlreadyExistsException
from app.auth.models import User, UserCreateRequest


async def create_user(db: AsyncSession, *, data: UserCreateRequest) -> User:
    """Creates a user in database

    Args:
        db (AsyncSession): Asynchronous Sqlalchemy database session object
        data (UserCreateRequest): UserCreateRequest pydantic schema

    Raises:
        HTTPException: Raise exception if the user with same email already exists

    Returns:
        User: returns newly created user
    """
    result = await db.execute(
        select(User).where(func.lower(User.email) == func.lower(data.email))
    )

    existing_user_obj = result.scalar_one_or_none()

    if existing_user_obj is not None:
        raise UserAlreadyExistsException(data.email)

    user_obj = User()
    user_obj.full_name = data.full_name
    user_obj.email = data.email

    user_obj.set_password(data.password)

    db.add(user_obj)

    await db.commit()
    await db.refresh(user_obj)

    return user_obj


async def authenticate_user(db: AsyncSession, *, email: str, password: str) -> User:
    """Get a user from DB and verifies password

    Args:
        db (AsyncSession): Asynchronous Sqlalchemy database session object
        email (str): email of the targer user
        password (str): password of the target user

    Raises:
        HTTPException: If the user is not authentic, HTTPException is raised

    Returns:
        User: Returns the user if authentic
    """
    result = await db.execute(select(User).where(User.email == email))

    user_obj = result.scalars().one_or_none()

    if user_obj is None:
        raise InvalidUsernamePasswordException()

    if not user_obj.verify_password(password):
        raise InvalidUsernamePasswordException()

    return user_obj
