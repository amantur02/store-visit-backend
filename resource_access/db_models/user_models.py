from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM

from resource_access.db_base_class import Base
from schemas.enums import UserRoleEnum


class UserDB(Base):
    __tablename__ = "users"

    first_name = Column(String(255))
    username = Column(String(255), nullable=False)
    role = Column(ENUM(UserRoleEnum, name="user_role_enum"))
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=True,
    )
