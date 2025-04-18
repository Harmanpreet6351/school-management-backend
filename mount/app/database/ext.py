from typing import cast
from fastapi import HTTPException
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(
    db: AsyncSession, stmt: Select, *, page: int = 1, per_page: int = 10
) -> dict:
    result = (
        await db.scalars(stmt.offset((page - 1) * per_page).limit(per_page))
    ).all()

    total_pages = await db.scalar(select(func.count()).select_from(stmt.subquery()))

    if total_pages is None:
        raise HTTPException(
            status_code=500, detail="Error fetching count from database"
        )

    return {
        "page": page,
        "total_pages": cast(int, total_pages),
        "data": cast(list, result),
    }
