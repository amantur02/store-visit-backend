from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from engines.auth_engines import AuthenticationEngine
from engines.order_engines import OrderEngine
from exceptions import DataValidationException, TimeIsUpException, AccessDeniedException
from resource_access.repositories.order_repos import OrderRepository, StoreRepository, VisitRepository
from resource_access.repositories.user_repos import UserRepository
from schemas.enums import OrderStatusEnum
from schemas.order_schemas import Order, OrderFilter, StoreFilter, Store, Visit, VisitFilter
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
    order_engine = OrderEngine
    await order_engine.validate_access_to_store(user, order.store_id)
    await order_engine.validate_worker_belonging(db_session, order.worker_id, order.store_id)

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


async def create_visit_usecase(db_session: Session, user: User, visit: Visit) -> Visit:
    order_repos = OrderRepository(db_session)
    order = await order_repos.get_order_by_id(visit.order_id)
    if order.expires_at > datetime.now():
        raise TimeIsUpException("Order receipt time")

    visit.store_id = order.store_id
    await OrderEngine.validate_access_to_store(user, visit.store_id)

    store_repos = VisitRepository(db_session)
    if await store_repos.get_visit_by_order_id(visit.order_id):
        raise AccessDeniedException("You cannot create visits already in a completed order")
    if user.id != order.customer_id:
        raise AccessDeniedException("You cannot create visits for another order(dont create order)")

    visit.worker_id = order.worker_id
    return await store_repos.create_visit(visit)


async def get_visits_usecase(db_session: Session, filters: VisitFilter) -> List[Visit]:
    visit_repo = VisitRepository(db_session)
    return await visit_repo.get_visits(filters)

