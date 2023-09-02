from sqlalchemy import String, Integer, Column, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from resource_access.db_base_class import Base
from schemas.enums import OrderStatusEnum
from .user_models import UserDB


class StoreDB(Base):
    __tablename__ = "stores"

    title = Column(String(255), nullable=False)

    products = relationship(
        'UserDb',
        back_populates='organization',
        lazy='selectin',
        uselist=True,
    )


class OrderDB(Base):
    __tablename__ = "orders"

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at = Column(TIMESTAMP)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    status = Column(ENUM(OrderStatusEnum, name="order_status_enum"))
    worker_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)


class VisitDB(Base):
    __tablename__ = "visits"

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    worker_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, unique=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False)
