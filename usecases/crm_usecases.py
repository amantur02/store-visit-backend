from sqlalchemy.orm import Session

from engines.auth_engines import AuthenticationEngine
from resource_access.repositories.user_repos import UserRepository
from schemas.user_schemas import User


async def create_user_usecase(db_session: Session, user: User, password: str):
    user.hashed_password = await AuthenticationEngine.get_password_hash(password)

    user_repo = UserRepository(db_session)
    return await user_repo.create_user(user)

