import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import NotFoundException
from resource_access.db_models.order_models import OrderDB, StoreDB
from schemas.order_schemas import Order, Store

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

