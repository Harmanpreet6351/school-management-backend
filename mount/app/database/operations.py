from typing import Any, Generic, Literal, Sequence, Type, TypedDict, TypeVar, cast

from fastapi import HTTPException, status
from sqlalchemy import ColumnElement, select, asc, desc
from sqlalchemy.orm import InstrumentedAttribute, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.core import Base
from app.database.ext import paginate as paginate_query

ModelType = TypeVar("ModelType", bound=Base)

FilterSpecDef = list[tuple[str, Literal["eq", "neq", "gt", "lt", "gte", "lte"], Any]]

OrderSpecDef = list[tuple[str, Literal["asc", "desc"]]]


class PaginationArgs(TypedDict):
    page: int
    per_page: int


async def db_get_item_by_filter_spec(
    db: AsyncSession,
    model: Type[ModelType],
    *,
    filter_spec: FilterSpecDef = [],
    order_spec: OrderSpecDef = [],
    pagination_data: PaginationArgs | None = None,
    joined_loan_cols: list[InstrumentedAttribute] = [],
    raw_filters: list[ColumnElement] = [],
    many: bool = True,
) -> dict | Sequence[ModelType] | ModelType | None:
    stmt = select(model)

    for spec in filter_spec:
        if hasattr(model, spec[0]):
            if spec[1] == "eq":
                stmt = stmt.where(getattr(model, spec[0]) == spec[2])
            elif spec[1] == "neq":
                stmt = stmt.where(getattr(model, spec[0]) != spec[2])
            elif spec[1] == "gt":
                stmt = stmt.where(getattr(model, spec[0]) > spec[2])
            elif spec[1] == "lt":
                stmt = stmt.where(getattr(model, spec[0]) < spec[2])
            elif spec[1] == "gte":
                stmt = stmt.where(getattr(model, spec[0]) >= spec[2])
            elif spec[1] == "lte":
                stmt = stmt.where(getattr(model, spec[0]) <= spec[2])

    if len(joined_loan_cols) > 0:
        stmt = stmt.options(joinedload(*joined_loan_cols))

    if len(raw_filters) > 0:
        stmt = stmt.where(*raw_filters)

    for spec in order_spec:
        if hasattr(model, spec[0]):
            if spec[1] == "asc":
                stmt = stmt.order_by(asc(getattr(model, spec[0])))
            elif spec[1] == "desc":
                stmt = stmt.order_by(desc(getattr(model, spec[0])))

    if pagination_data is not None:
        return await paginate_query(
            db,
            stmt,
            page=pagination_data["page"],
            per_page=pagination_data["per_page"] or 10,
        )

    result = await db.execute(stmt)

    if not many:
        obj = result.scalar_one_or_none()

        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{obj.__class__} not Found",
            )

        return obj

    else:
        return result.scalars().all()


class QueryExecutor(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        *,
        filter_spec: FilterSpecDef = [],
        order_spec: OrderSpecDef = [],
        pagination_data: PaginationArgs | None = None,
        joined_loan_cols: list[InstrumentedAttribute] = [],
        raw_filters: list[ColumnElement] = [],
    ) -> None:
        self.model_name = str(model.__class__)
        self.filter_spec = filter_spec

        self.stmt = select(model)

        for spec in filter_spec:
            if hasattr(model, spec[0]):
                if spec[1] == "eq":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) == spec[2])
                elif spec[1] == "neq":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) != spec[2])
                elif spec[1] == "gt":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) > spec[2])
                elif spec[1] == "lt":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) < spec[2])
                elif spec[1] == "gte":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) >= spec[2])
                elif spec[1] == "lte":
                    self.stmt = self.stmt.where(getattr(model, spec[0]) <= spec[2])

        if len(joined_loan_cols) > 0:
            self.stmt = self.stmt.options(joinedload(*joined_loan_cols))

        if len(raw_filters) > 0:
            self.stmt = self.stmt.where(*raw_filters)

        for spec in order_spec:
            if hasattr(model, spec[0]):
                if spec[1] == "asc":
                    self.stmt = self.stmt.order_by(asc(getattr(model, spec[0])))
                elif spec[1] == "desc":
                    self.stmt = self.stmt.order_by(desc(getattr(model, spec[0])))

    async def paginate(self, db: AsyncSession, pagination_data: PaginationArgs) -> dict:
        return await paginate_query(
            db,
            self.stmt,
            page=pagination_data["page"],
            per_page=pagination_data["per_page"] or 10,
        )

    async def get_one(self, db: AsyncSession) -> ModelType | None:
        result = await db.execute(self.stmt)

        return result.scalar_one_or_none()

    async def get_one_or_404(self, db: AsyncSession) -> ModelType:
        obj = await self.get_one(db)

        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "msg": f"{self.model_name} not found",
                    "filter_spec": self.filter_spec,
                },
            )

        return obj

    async def get_many(self, db: AsyncSession) -> list[ModelType]:
        result = await db.execute(self.stmt)

        return cast(list[ModelType], result.scalars().all())


async def create_item_from_json(
    db: AsyncSession, model: Type[ModelType], data: dict
) -> ModelType:
    obj = model()
    for key, val in data.items():
        if hasattr(obj, key):
            setattr(obj, key, val)

    db.add(obj)
    await db.commit()

    await db.refresh(obj)

    return obj
