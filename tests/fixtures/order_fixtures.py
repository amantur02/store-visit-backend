from datetime import datetime

import pytest

from resource_access.db_models.order_models import OrderDB
from schemas.enums import OrderStatusEnum


@pytest.fixture(scope="function")
async def user(db_session):
    date = datetime.now()
    order_db = OrderDB(
        id=1,
        created_at=date,
        expires_at=date,
        store_id=1,
        worker_id=1,
        customer_id=1,
        status=OrderStatusEnum.started
    )
    db_session.add(order_db)
    await db_session.commit()
    await db_session.refresh(order_db)
    yield order_db
