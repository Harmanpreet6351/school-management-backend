from fastapi import status

from app.exceptions.base_exception import AppBaseException


class UserAlreadyExistsException(AppBaseException):

    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_ALREADY_EXISTS",
            detail=f"User with {email} already exists"
        )

class InvalidUsernamePasswordException(AppBaseException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_USER_CREDS",
            detail="Invalid username or password"
        )