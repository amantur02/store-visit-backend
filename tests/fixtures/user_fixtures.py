import pytest

from engines.auth_engines import AuthenticationEngine
from resource_access.db_models.user_models import UserDB
from schemas.enums import UserRoleEnum


@pytest.fixture(scope="function")
async def user(db_session):
    hashed_password = await AuthenticationEngine.get_password_hash("password")
    user_db = UserDB(
        first_name="Test Name",
        username="996777112233",
        role=UserRoleEnum.customer,
        hashed_password=hashed_password,
    )
    db_session.add(user_db)
    await db_session.commit()
    await db_session.refresh(user_db)
    yield user_db


@pytest.fixture(scope="function")
async def user_worker(db_session):
    hashed_password = await AuthenticationEngine.get_password_hash("password")
    user_db = UserDB(
        first_name="Test Name",
        username="996777112233",
        role=UserRoleEnum.worker,
        hashed_password=hashed_password,
    )
    db_session.add(user_db)
    await db_session.commit()
    await db_session.refresh(user_db)
    yield user_db

