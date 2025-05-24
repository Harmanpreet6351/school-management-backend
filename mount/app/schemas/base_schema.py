from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

APIResponseModel = TypeVar("APIResponseModel")


class DBBaseModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class _ErrorResponseBodyModel(BaseModel):
    code: str = Field(..., examples=["ERROR_CODE"])
    detail: str = Field(..., examples=["Default error"])

class ErrorResponseModel(BaseModel):
    error: _ErrorResponseBodyModel

class BaseResponseModel(BaseModel, Generic[APIResponseModel]):
    meta: dict | None = Field({}, examples=[{}])
    data: APIResponseModel | None = None