from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field
from app.database.core import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


class PaginationParams(BaseModel):
    page: int = Field(..., description="Page number")
    per_page: int = Field(10, description="Number of itmes to show per page")


async def async_get_db():
    async with AsyncSessionLocal() as db:
        yield db


AsyncSessionDep = Annotated[AsyncSession, Depends(async_get_db)]

PaginationParamsDep = Annotated[PaginationParams, Query()]
