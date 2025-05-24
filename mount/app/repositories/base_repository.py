from typing import Any, Generic, Type, TypeVar, cast
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_, insert

from app.database.core import Base

# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        Async CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        Get a single record by ID
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """
        Get multiple records with pagination
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return cast(list[ModelType], result.scalars().all())

    async def get_by_attribute(
        self, db: AsyncSession, *, attribute: str, value: Any
    ) -> ModelType | None:
        """
        Get a single record by any attribute
        """
        stmt = select(self.model).where(getattr(self.model, attribute) == value)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_by_attribute(
        self, db: AsyncSession, *, attribute: str, value: Any, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """
        Get multiple records by any attribute with pagination
        """
        stmt = (
            select(self.model)
            .where(getattr(self.model, attribute) == value)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return cast(list[ModelType], result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: BaseModel | dict) -> ModelType:
        """
        Create a new record
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_multi(self, db: AsyncSession, *, objs_in: list[BaseModel | dict]) -> list[ModelType]:
        """
        Create multiple records
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)
            db.add(db_obj)
        
        await db.commit()
        for db_obj in db_objs:
            await db.refresh(db_obj)
        return db_objs

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: BaseModel | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = jsonable_encoder(obj_in)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_by_id(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: BaseModel | dict[str, Any]
    ) -> ModelType | None:
        """
        Update a record by ID
        """
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)
        return None

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        """
        Delete a record by ID
        """
        db_obj = await self.get(db=db, id=id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
            return db_obj
        return None

    async def delete_multi(self, db: AsyncSession, *, ids: list[Any]) -> int:
        """
        Delete multiple records by IDs
        Returns the number of deleted records
        """
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def count(self, db: AsyncSession) -> int:
        """
        Count total records
        """
        stmt = select(func.count(self.model.id))
        result = await db.execute(stmt)
        return cast(int, result.scalar())

    async def exists(self, db: AsyncSession, *, id: Any) -> bool:
        """
        Check if a record exists by ID
        """
        stmt = select(self.model.id).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.first() is not None

    async def get_or_create(
        self, 
        db: AsyncSession, 
        *, 
        defaults: dict[str, Any] | None = None,
        **kwargs
    ) -> tuple[ModelType, bool]:
        """
        Get an existing record or create a new one
        Returns tuple of (object, created_flag)
        """
        # Build the where clause dynamically
        conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
        stmt = select(self.model).where(and_(*conditions))
        result = await db.execute(stmt)
        instance = result.scalar_one_or_none()
        
        if instance:
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.items())
            if defaults:
                params.update(defaults)
            instance = self.model(**params)
            db.add(instance)
            await db.commit()
            await db.refresh(instance)
            return instance, True

    async def bulk_create(self, db: AsyncSession, *, objs_in: list[BaseModel | dict]) -> None:
        """
        Bulk create records (more efficient for large datasets)
        Note: This doesn't return the created objects or trigger refresh
        """
        objects_data = [jsonable_encoder(obj) for obj in objs_in]
        await db.execute(insert(self.model), objects_data)
        await db.commit()

    async def filter_by(
        self,
        db: AsyncSession,
        *,
        filters: dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None
    ) -> list[ModelType]:
        """
        Filter records by multiple attributes
        """
        stmt = select(self.model)
        
        # Apply filters
        for attr, value in filters.items():
            if hasattr(self.model, attr):
                stmt = stmt.where(getattr(self.model, attr) == value)
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return cast(list[ModelType], result.scalars().all())