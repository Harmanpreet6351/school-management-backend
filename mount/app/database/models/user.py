import bcrypt

from datetime import datetime, timedelta, timezone
from sqlalchemy import String
from app.core.config import get_settings
from app.database.core import Base
from sqlalchemy.orm import Mapped, mapped_column
from jose import jwt, ExpiredSignatureError, JWTError

class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)

    @property
    def token(self):
        expire = datetime.now(timezone.utc) + timedelta(minutes=get_settings().jwt_expiration_minutes)
        to_encode = {
            "sub": str(self.id),
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, get_settings().jwt_secret_key)
        return encoded_jwt

    def set_password(self, password: str) -> None:
        pw = password.encode()
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(pw, salt).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
    
    @staticmethod
    def verify_token(token: str) -> dict | None:
        """
        Verifies the JWT token and returns the decoded payload if valid.

        Raises:
            ExpiredSignatureError: if the token has expired.
            JWTError: if the token is invalid.
        """
        try:
            payload = jwt.decode(token, get_settings().jwt_secret_key)
            return payload
        except ExpiredSignatureError:
            print("Token has expired.")
        except JWTError:
            print("Invalid token.")
        return None