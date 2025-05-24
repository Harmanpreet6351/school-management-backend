from typing import Generic, TypeVar
from pydantic import BaseModel, Field

PaginatedData = TypeVar("PaginatedData")

class PaginationParams(BaseModel):
    page: int = Field(..., description="Page number")
    per_page: int = Field(10, description="Number of itmes to show per page")


class PaginatedResponse(BaseModel, Generic[PaginatedData]):
    page: int
    total_pages: int
    data: list[PaginatedData] = Field([])