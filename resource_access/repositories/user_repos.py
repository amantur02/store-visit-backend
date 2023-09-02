from sqlalchemy import select
from sqlalchemy.orm import Session

from exceptions import NotFoundException
from resource_access.db_models.user_models import UserDB
from schemas.user_schemas import User


class UserRepository:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def get_user_by_username(self, username: str) -> User:
        query = await self._db_session.execute(
            select(UserDB).where(
                UserDB.username == username, UserDB.is_deleted.is_(False)
            )
        )
        user_db = query.scalar()
        if user_db:
            return User.model_validate(user_db)
        raise NotFoundException(f"Does not exist user with username: {username}")

    async def get_user_by_id(self, user_id: int) -> User:
        query = await self._db_session.execute(
            select(UserDB).where(
                UserDB.id == user_id, UserDB.is_deleted.is_(False)
            )
        )
        user_db = query.scalar()
        if user_db:
            return User.model_validate(user_db)
        raise NotFoundException(f"Not found user with id: {user_id}")
