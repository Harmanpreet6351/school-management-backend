from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

PaginatedData = TypeVar("PaginatedData")


class DBBaseModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel, Generic[PaginatedData]):
    page: int
    total_pages: int
    data: list[PaginatedData] = Field([])
