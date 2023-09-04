import logging
from typing import List
from pydantic.tools import parse_obj_as

from psycopg2.errorcodes import UNIQUE_VIOLATION
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import NotFoundException, AlreadyExistsException
from resource_access.db_models.user_models import UserDB
from schemas.user_schemas import User, UserFilter

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def create_user(
        self, user: User
    ) -> User:
        user_db = UserDB(
            **user.model_dump(exclude_unset=True, exclude={'id'}),
        )
        self._db_session.add(user_db)
        try:
            await self._db_session.commit()
            await self._db_session.refresh(user_db)
            return User.model_validate(user_db)
        except IntegrityError as e:
            logger.error(
                f"Error while creating User, details: {e.orig.args}"
            )
            await self._db_session.rollback()
            if e.orig.sqlstate == UNIQUE_VIOLATION:
                if "username" in e.orig.args[0]:
                    raise AlreadyExistsException(
                        f"User with username '{user.username}' already exist"
                    )

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

    async def get_users(self, filters: UserFilter) -> List[User]:
        where_args = [
            UserDB.is_deleted.is_(False),
        ]
        if filters.first_name:
            where_args.append(UserDB.first_name == filters.first_name)
        elif filters.username:
            where_args.append(UserDB.username == filters.username)

        stmt = (
            select(UserDB)
            .where(*where_args)
            .order_by(UserDB.id.desc())
        )

        query = await self._db_session.execute(stmt)
        return parse_obj_as(List[User], query.scalars().all())
