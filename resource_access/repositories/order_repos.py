import logging
from typing import List

from pydantic.tools import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import NotFoundException
from resource_access.db_models.order_models import OrderDB, StoreDB
from schemas.enums import UserRoleEnum
from schemas.order_schemas import Order, Store, OrderFilter
from schemas.user_schemas import User

logger = logging.getLogger(__name__)


class OrderRepository:

    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def create_order(
        self, order: Order
    ) -> Order:
        order_db = OrderDB(
            **order.model_dump(exclude={"id"})
        )
        self._db_session.add(order_db)

        try:
            await self._db_session.commit()
            await self._db_session.refresh(order_db)
            return Order.model_validate(order_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating Organization. Details: {error.orig.args}"
            )
            await self._db_session.rollback()

    async def get_products(self, filters: OrderFilter, user: User) -> List[Order]:
        where_args = [
            OrderDB.is_deleted.is_(False),
            OrderDB.status == filters.status
        ]
        if user.role == UserRoleEnum.customer:
            where_args.append(OrderDB.customer_id == user.id)
        elif user.role == UserRoleEnum.worker:
            where_args.append(OrderDB.worker_id == user.id)

        stmt = (
            select(OrderDB)
            .where(*where_args)
            .order_by(OrderDB.id.desc())
        )

        query = await self._db_session.execute(stmt)
        return parse_obj_as(List[Order], query.scalars().all())


class StoreRepository:

    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def get_store_by_id(self, store_id: int) -> Store:
        stmt = select(StoreDB).where(
            StoreDB.id == store_id,
            StoreDB.is_deleted.is_(False),
        )
        query = await self._db_session.execute(stmt)
        product_db = query.scalar()

        if product_db:
            return product_db
        raise NotFoundException(f"Does not store with id: {store_id}")

