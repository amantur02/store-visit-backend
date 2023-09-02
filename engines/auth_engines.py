from exceptions import AuthenticationError
from schemas.user_schemas import User
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationEngine:
    @staticmethod
    async def validate_password(user: User, password: str):
        valid = False
        if user.hashed_password:
            valid = pwd_context.verify(password, user.hashed_password)
        if not valid:
            raise AuthenticationError(message="Wrong password")

    @staticmethod
    async def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
