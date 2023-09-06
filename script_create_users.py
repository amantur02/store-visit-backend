import asyncio
import logging
import httpx
import random
from faker import Faker
from sqlalchemy.orm import Session
from resource_access.db_models.order_models import StoreDB
from resource_access.db_session import AsyncSessionLocal
from schemas.enums import UserRoleEnum

fake = Faker()
logger = logging.getLogger(__name__)


async def create_store_with_session():
    async with AsyncSessionLocal() as session:
        await create_store(session, 'store 1')


async def create_store(session: Session, store_title: str):
    store_db = StoreDB(
        title=store_title
    )
    session.add(store_db)
    await session.flush()
    await session.commit()


API_BASE_URL = "http://localhost:8000/api/crm"


async def create_user(username, first_name, role, store_id, password):
    async with httpx.AsyncClient() as client:
        user_data = {
            "username": username,
            "first_name": first_name,
            "role": role,
            "store_id": store_id,
            "password": password
        }
        response = await client.post(f"{API_BASE_URL}/create-user/", json=user_data)
        print(f"User with id created: {response.json()['id']}")
        return response


def generate_random_user():
    username = fake.user_name()
    first_name = fake.first_name()
    role = random.choice([r.value for r in UserRoleEnum])
    store_id = 1
    password = fake.password()
    return username, first_name, role, store_id, password


async def main():
    await create_store_with_session()
    tasks = []
    rate_limit = 3  # Ограничение в 3 запроса в секунду
    for _ in range(300):
        username, first_name, role, store_id, password = generate_random_user()
        task = create_user(username, first_name, role, store_id, password)
        tasks.append(task)
        if len(tasks) >= rate_limit:
            await asyncio.gather(*tasks)
            tasks = []
            await asyncio.sleep(1)

    if tasks:
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
