from pydantic import BaseModel, ConfigDict, Field
from app.schemas.base_schema import DBBaseModel


class UserRead(DBBaseModel):
    full_name: str
    email: str
    password_hash: str


class UserCreateRequest(BaseModel):
    full_name: str = Field(..., examples=["John Doe"])
    email: str = Field(..., examples=['john@example.com'])
    password: str = Field(..., examples=['topsecret'])


class TokenResponse(BaseModel):
    access_token: str
    user: UserRead

    model_config = ConfigDict(from_attributes=True)


class TokenRequest(BaseModel):
    email: str = Field(..., examples=['john@example.com'])
    password: str = Field(..., examples=['topsecret'])