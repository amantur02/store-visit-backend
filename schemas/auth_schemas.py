from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: int


class TokenSchema(BaseModel):
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str]
