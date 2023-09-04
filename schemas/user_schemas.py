from pydantic import BaseModel
from typing import Optional

from .enums import UserRoleEnum


class User(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    store_id: Optional[int] = None
    hashed_password: Optional[str] = None

    class Config:
        from_attributes = True


class UserIn(BaseModel):
    username: str
    first_name: str
    role: UserRoleEnum
    store_id: int
    password: str


class UserOut(BaseModel):
    username: str
    first_name: str
    role: UserRoleEnum
    store_id: int


class UserLoginIn(BaseModel):
    username: str
    password: str


class UserFilter(BaseModel):
    first_name: Optional[str] = None
    username: Optional[str] = None
