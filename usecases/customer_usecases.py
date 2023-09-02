from sqlalchemy.orm import Session

from engines.auth_engines import AuthenticationEngine
from resource_access.repositories.order_repos import OrderRepository
from resource_access.repositories.user_repos import UserRepository
from schemas.order_schemas import Order
from core.jwt_tokens import create_access_token, create_refresh_token


async def user_login_usecase(db_session: Session, username: str, password: str):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_user_by_username(username)

    await AuthenticationEngine.validate_password(user, password)

    return {
        "access_token": create_access_token(user_id=user.id),
        "refresh_token": create_refresh_token(user_id=user.id),
        "token_type": "bearer",
    }


async def create_order_usecase(db_session: Session, order: Order) -> Order:
    order_repos = OrderRepository(db_session)

    return await order_repos.create_order(order)
