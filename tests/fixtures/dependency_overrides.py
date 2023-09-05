from schemas.enums import UserRoleEnum
from schemas.user_schemas import User

user = User(
    id=1,
    username="test",
    first_name="Test",
    role=UserRoleEnum.customer,
    store_id=1
)
user_customer = User(
    id=1,
    username="test",
    first_name="Test",
    role=UserRoleEnum.customer,
    store_id=1
)


async def get_user_override() -> User:
    return user


async def get_current_customer_override() -> User:
    return user_customer
