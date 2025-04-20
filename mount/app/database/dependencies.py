from typing import Annotated

from fastapi import Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession


class PaginationParams(BaseModel):
    page: int = Field(..., description="Page number")
    per_page: int = Field(10, description="Number of itmes to show per page")


async def async_get_db(request: Request):
    async with AsyncSession(request.app.state.db_pool) as db:
        yield db


AsyncSessionDep = Annotated[AsyncSession, Depends(async_get_db)]

PaginationParamsDep = Annotated[PaginationParams, Query()]
