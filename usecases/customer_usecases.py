from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from engines.auth_engines import AuthenticationEngine
from exceptions import DataValidationException
from resource_access.repositories.order_repos import OrderRepository, StoreRepository
from resource_access.repositories.user_repos import UserRepository
from schemas.order_schemas import Order, OrderFilter, StoreFilter, Store
from core.jwt_tokens import create_access_token, create_refresh_token
from schemas.user_schemas import User


async def user_login_usecase(db_session: Session, username: str, password: str):
    user_repo = UserRepository(db_session)
    user = await user_repo.get_user_by_username(username)

    await AuthenticationEngine.validate_password(user, password)

    return {
        "access_token": create_access_token(user_id=user.id),
        "refresh_token": create_refresh_token(user_id=user.id),
        "token_type": "bearer",
    }


async def create_order_usecase(db_session: Session, order: Order, user: User) -> Order:
    store_repos = StoreRepository(db_session)
    store = await store_repos.get_store_by_id(order.store_id)

    if user.store_id != order.store_id:
        raise DataValidationException(message="You cannot create an order for another store")
    if order.worker_id not in [user.id for user in store.users]:
        raise DataValidationException(message="You cannot create an order for employee from another store")

    order.customer_id = user.id
    order.expires_at = order.expires_at.replace(tzinfo=None)
    order_repos = OrderRepository(db_session)
    return await order_repos.create_order(order)


async def get_orders_usecase(db_session: Session, filters: OrderFilter, user: User) -> List[Order]:
    order_repos = OrderRepository(db_session)
    return await order_repos.get_orders(filters, user)


async def update_order_usecase(db_session: Session, order: Order) -> Order:
    order_repo = OrderRepository(db_session)
    return await order_repo.update_order(order)


async def delete_order_usecase(db_session: Session, order_id: int) -> None:
    order_repo = OrderRepository(db_session)
    return await order_repo.delete_order(order_id)


async def get_stores_usecase(db_session: Session, filters: StoreFilter) -> List[Store]:
    store_repo = StoreRepository(db_session)
    return await store_repo.get_stores(filters)
