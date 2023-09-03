from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel

from schemas.enums import OrderStatusEnum
from schemas.user_schemas import User


class Order(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    store_id: Optional[int] = None
    customer_id: Optional[int] = None
    status: Optional[OrderStatusEnum] = None
    worker_id: Optional[int] = None

    class Config:
        from_attributes = True


class Store(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    users: Optional[User] = None

    class Config:
        from_attributes = True


expires_at = datetime(2023, 9, 3, 9, 29, 6, tzinfo=timezone.utc)


class OrderIn(BaseModel):
    expires_at: datetime
    store_id: int
    worker_id: int


class OrderOut(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    store_id: int
    customer_id: int
    status: OrderStatusEnum
    worker_id: int


class OrderFilter(BaseModel):
    my_order: bool
    status: OrderStatusEnum
