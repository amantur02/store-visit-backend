from sqlalchemy.orm import Session

from exceptions import DataValidationException
from resource_access.repositories.order_repos import StoreRepository
from schemas.user_schemas import User


class OrderEngine:
    @classmethod
    async def validate_access_to_store(cls, user: User, store_id: int) -> None:
        if user.store_id != store_id:
            raise DataValidationException(message="You cannot create an order for another store")

    @classmethod
    async def validate_worker_belonging(cls, db_session: Session, worker_id: int, store_id: int) -> None:
        store_repos = StoreRepository(db_session)
        store = await store_repos.get_store_by_id(store_id)

        if worker_id not in [user.id for user in store.users]:
            raise DataValidationException(message="You cannot create an order for employee from another store")

