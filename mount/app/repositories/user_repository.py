
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user_schema import UserCreateRequest


class UserRepository(BaseRepository[User]):
    
    async def create_with_hash(self, db: AsyncSession, *, obj: UserCreateRequest) -> User:
        
        user_obj = User()
        user_obj.email = obj.email
        user_obj.full_name = obj.full_name
        user_obj.set_password(obj.password)
        
        db.add(user_obj)

        await db.commit()
        await db.refresh(user_obj)

        return user_obj

user_repo = UserRepository(User)