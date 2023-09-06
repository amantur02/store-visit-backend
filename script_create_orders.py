import asyncio
import logging
import httpx
import random
from faker import Faker
from sqlalchemy.orm import Session
from resource_access.db_models.order_models import StoreDB
from resource_access.db_models.user_models import UserDB
from resource_access.db_session import AsyncSessionLocal
from datetime import datetime, timedelta

from schemas.enums import UserRoleEnum

fake = Faker()
logger = logging.getLogger(__name__)
API_BASE_URL = "http://localhost:8000/api"


async def create_store():
    async with AsyncSessionLocal() as session:
        store_db = StoreDB(
            title="store_title"
        )
        session.add(store_db)
        await session.flush()
        await session.commit()

    return store_db


async def create_user(username, first_name, role, store_id, password):
    async with httpx.AsyncClient() as client:
        user_data = {
            "username": username,
            "first_name": first_name,
            "role": role,
            "store_id": store_id,
            "password": password
        }
        response = await client.post(f"{API_BASE_URL}/crm/create-user/", json=user_data)
        return response


async def login_and_get_token(username, password):
    async with httpx.AsyncClient() as client:
        login_data = {
            "username": username,
            "password": password
        }
        response = await client.post(f"{API_BASE_URL}/auth/login/", json=login_data)
        return response.json()


async def create_order_with_customer(store_id, token):
    async with httpx.AsyncClient() as client:
        order_data = {
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "store_id": store_id,
            "worker_id": 1
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(f"{API_BASE_URL}/customers/create-order/", json=order_data, headers=headers)
        return response


async def generate_random_user():
    username = fake.user_name()
    first_name = fake.first_name()
    password = fake.password()
    return username, first_name, password


async def main():
    rate_limit = 3

    store = await create_store()
    username, first_name, password = await generate_random_user()
    create_user_response = await create_user(username, first_name, UserRoleEnum.customer, store.id, password)

    username_work, first_name_work, password_work = await generate_random_user()
    await create_user(username_work, first_name_work, UserRoleEnum.worker, store.id, password_work)
    if create_user_response.status_code == 201:
        token_response = await login_and_get_token(username, password)
        token = token_response.get("access_token")

        tasks = []
        for _ in range(300):
            task_order = create_order_with_customer(store.id, token)
            tasks.append(task_order)

            if len(tasks) >= rate_limit:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)

        if tasks:
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
