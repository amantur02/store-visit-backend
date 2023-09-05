from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

ASYNC_TEST_DB_URL = f"{settings.postgres_async_url}"
TEST_DB_URL = f"{settings.postgres_url}"

async_engine = create_async_engine(ASYNC_TEST_DB_URL, echo=True)
sync_engine = create_engine(TEST_DB_URL)

AsyncTestSession = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autocommit=False,
    class_=AsyncSession,
)
TestSession = sessionmaker(bind=sync_engine)
