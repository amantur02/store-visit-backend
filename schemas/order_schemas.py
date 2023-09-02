from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.enums import OrderStatusEnum


class Order(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    store_id: Optional[int] = None
    customer_id: Optional[int] = None
    status: Optional[OrderStatusEnum] = None
    worked_id: Optional[int] = None

    class Config:
        from_attributes = True


class OrderIn(BaseModel):
    expires_at: datetime
    store_id: int
    worked_id: int


class OrderOut(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    store_id: int
    customer_id: int
    status: OrderStatusEnum
    worked_id: int

