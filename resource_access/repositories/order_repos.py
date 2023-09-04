import logging
from typing import List

from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION, UNIQUE_VIOLATION
from pydantic.tools import parse_obj_as
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from exceptions import NotFoundException, AlreadyExistsException
from resource_access.db_models.order_models import OrderDB, StoreDB, VisitDB
from schemas.enums import UserRoleEnum
from schemas.order_schemas import Order, Store, OrderFilter, StoreFilter, Visit, VisitFilter
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
                f"Error while creating Order. Details: {error.orig.args}"
            )
            await self._db_session.rollback()
            await self.__integrity_error_handler(error, order)

    async def get_orders(self, filters: OrderFilter, user: User) -> List[Order]:
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

    async def update_order(self, order: Order) -> Order:
        await self.get_order_by_id(order.id)
        try:
            query = await self._db_session.execute(
                update(OrderDB)
                .where(OrderDB.id == order.id)
                .values(**order.model_dump(exclude_unset=True, exclude={"id", "created_at"}))
                .returning(OrderDB)
            )
            await self._db_session.commit()
            order_db, = query.one()  # Unpacking the tuple
            return Order.model_validate(order_db)
        except IntegrityError as error:
            logger.error(
                f"Error while updating Order. Details: {error.orig.args}"
            )
            await self._db_session.rollback()
            await self.__integrity_error_handler(error, order)

    async def delete_order(
        self, order_id: int
    ) -> None:
        order_db = await self.get_order_by_id(
            order_id
        )
        order_db.is_deleted = True
        await self._db_session.commit()

    async def get_order_by_id(self, order_id: int) -> Order:
        stmt = select(OrderDB).where(
            OrderDB.id == order_id, OrderDB.is_deleted.is_(False)
        )

        query = await self._db_session.execute(stmt)
        order_db = query.scalar()

        if order_db:
            return order_db
        raise NotFoundException(f"There is no order with this id: {order_id}")

    # async def update_order_status(self, order: Order) -> Order:
    #     await self.get_order_by_id(order.id)
    #     query = await self._db_session.execute(
    #         update(OrderDB)
    #         .where(OrderDB.id == order.id)
    #         .values(status=order.status)
    #         .returning(OrderDB)
    #     )
    #     await self._db_session.commit()
    #     order_db, = query.one()
    #     return Order.model_validate(order_db)

    async def __integrity_error_handler(self, e, order) -> None:
        if e.orig.sqlstate == FOREIGN_KEY_VIOLATION:
            if "worker_id" in e.orig.args[0]:
                raise NotFoundException(
                    f"Does not worker with id: {order.worker_id}"
                )
            if "store_id" in e.orig.args[0]:
                raise NotFoundException(
                    f"Does not store with id: {order.store_id}"
                )


class StoreRepository:

    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def get_store_by_id(self, store_id: int) -> Store:
        stmt = select(StoreDB).where(
            StoreDB.id == store_id,
            StoreDB.is_deleted.is_(False),
        )
        query = await self._db_session.execute(stmt)
        store_db = query.scalar()

        if store_db:
            return store_db
        raise NotFoundException(f"Does not store with id: {store_id}")

    async def get_stores(self, filters: StoreFilter) -> List[Store]:
        where_args = [StoreDB.is_deleted.is_(False)]

        if filters.id is not None:
            where_args.append(StoreDB.id == filters.id)

        if filters.title:
            where_args.append(StoreDB.title.like(f"%{filters.title}%"))

        stmt = (
            select(StoreDB)
            .where(*where_args)
            .order_by(StoreDB.id.desc())
        )

        query = await self._db_session.execute(stmt)
        return parse_obj_as(List[Store], query.scalars().all())


class VisitRepository:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    async def create_visit(
            self, visit: Visit
    ) -> Visit:
        visit_db = VisitDB(
            **visit.model_dump(exclude={"id"})
        )
        self._db_session.add(visit_db)

        try:
            await self._db_session.commit()
            await self._db_session.refresh(visit_db)
            return Visit.model_validate(visit_db)
        except IntegrityError as error:
            logger.error(
                f"Error while creating Visit. Details: {error.orig.args}"
            )
            await self._db_session.rollback()
            await self.__integrity_error_handler(error, visit)

    async def get_visit_by_order_id(self, order_id: int) -> Visit:
        stmt = select(VisitDB).where(
            VisitDB.order_id == order_id,
            VisitDB.is_deleted.is_(False),
        )
        query = await self._db_session.execute(stmt)
        visit_db = query.scalar()

        return visit_db

    async def get_visits(self, filters: VisitFilter) -> List[Visit]:
        where_args = [
            VisitDB.is_deleted.is_(False),
        ]
        if filters.order_id:
            where_args.append(VisitDB.order_id == filters.order_id)

        stmt = (
            select(VisitDB)
            .where(*where_args)
            .order_by(VisitDB.id.desc())
        )

        query = await self._db_session.execute(stmt)
        return parse_obj_as(List[Visit], query.scalars().all())

    async def delete_visit(
        self, visit_id: int
    ) -> None:
        visit_db = await self.get_visit_by_order_id(
            visit_id
        )
        visit_db.is_deleted = True
        await self._db_session.commit()

    async def __integrity_error_handler(self, e, visit: Visit) -> None:
        if e.orig.sqlstate == FOREIGN_KEY_VIOLATION:
            if "worker_id" in e.orig.args[0]:
                raise NotFoundException(
                    f"Does not worker with id: {visit.worker_id}"
                )
            if "order_id" in e.orig.args[0]:
                raise NotFoundException(
                    f"Does not order with id: {visit.order_id}"
                )
            if "store_id" in e.orig.args[0]:
                raise NotFoundException(
                    f"Does not store with id: {visit.store_id}"
                )
        if e.orig.sqlstate == UNIQUE_VIOLATION:
            if "order_id" in e.orig.args[0]:
                raise AlreadyExistsException(
                    f"Visit with order id: {visit.order_id} already exist"
                )

