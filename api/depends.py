from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status

from core.config import settings
from resource_access.db_session import AsyncSessionLocal
#
# oauth2_schema = OAuth2PasswordBearer(
#     tokenUrl=f"{settings.api_path}/auth/login/"
# )


async def get_session() -> Session:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# async def get_phone_number(token: str = Depends(oauth2_schema)):
#     try:
#         print(token)
#     except (ValidationError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             headers={"WWW-Authenticate": "Bearer"},
#         )
