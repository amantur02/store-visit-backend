import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from resource_access.db_models.order_models import OrderDB
from schemas.order_schemas import Order

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
