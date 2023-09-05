import asyncio
import sqlite3

import aiosqlite
import pytest
from api.depends import get_current_user, get_session, get_current_customer
from httpx import AsyncClient
from main import app
from resource_access.db_base import *
from tests.fixtures.dependency_overrides import (
    get_current_customer_override,
    get_user_override,
)

from .common_setup import (AsyncTestSession, TestSession, async_engine,
                           sync_engine)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session(event_loop):
    connection = await async_engine.connect()
    await connection.begin()
    session = AsyncTestSession(bind=connection)
    yield session
    # Rollback the overall transaction, restoring the state before the test ran.
    await session.close()
    await connection.close()


@pytest.fixture(scope="function")
def sync_db_session():
    connection = sync_engine.connect()
    connection.begin()
    session = TestSession(bind=connection)
    yield session
    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def db_sqlite_sync_session(event_loop):
    with sqlite3.connect(":memory:") as db:
        yield db


@pytest.fixture(scope="function")
async def client(db_session):
    async def test_session():
        yield db_session

    app.dependency_overrides[get_session] = test_session
    app.dependency_overrides[get_current_user] = get_user_override
    app.dependency_overrides[get_current_customer] = get_current_customer_override

    async with AsyncClient(
        app=app, base_url="http://127.0.0.1:8000/api"
    ) as ac:
        yield ac
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
async def db_sqlite_session(event_loop):
    async with aiosqlite.connect(":memory:") as db:
        yield db


@pytest.fixture(scope="function")
async def sqlite_client(db_sqlite_session):
    async def test_session():
        yield db_sqlite_session
    app.dependency_overrides[get_session] = test_session
    app.dependency_overrides[get_current_user] = get_user_override
    app.dependency_overrides[get_current_customer] = get_current_customer_override

    async with AsyncClient(
        app=app, base_url="http://127.0.0.1:5000/api"
    ) as ac:
        yield ac
    app.dependency_overrides = {}
