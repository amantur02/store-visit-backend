from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt

from core.config import settings
from core.constants import JWT_ALGORITHM, INVALID_AUTHENTICATION_CREDENTIALS
from exceptions import NotFoundException
from resource_access.db_session import AsyncSessionLocal
from resource_access.repositories.user_repos import UserRepository
from schemas.auth_schemas import TokenPayload
from schemas.user_schemas import User

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_path}/auth/login/"
)


async def get_session() -> Session:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_token_data(token: str = Depends(oauth2_schema)) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.access_token_secret_key,
            algorithms=[JWT_ALGORITHM],
        )
        return TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_AUTHENTICATION_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: TokenPayload = Depends(get_token_data),
    db_session: Session = Depends(get_session),
) -> User:
    try:
        user_repo = UserRepository(db_session)
        user_from_repo = await user_repo.get_user_by_id(token.sub)
        return user_from_repo
    except NotFoundException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_AUTHENTICATION_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
