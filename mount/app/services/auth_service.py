from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.exceptions.user_exception import InvalidUsernamePasswordException, UserAlreadyExistsException
from app.schemas.user_schema import UserCreateRequest
from app.repositories.user_repository import user_repo


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

    existing_user_obj = await user_repo.get_by_attribute(db, attribute="email", value=data.email)

    if existing_user_obj is not None:
        raise UserAlreadyExistsException(data.email)

    return await user_repo.create_with_hash(db, obj=data)


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

    user_obj = await user_repo.get_by_attribute(db, attribute="email", value=email)

    if user_obj is None:
        raise InvalidUsernamePasswordException()

    if not user_obj.verify_password(password):
        raise InvalidUsernamePasswordException()

    return user_obj
