import os
from typing import List, Union

from core.constants import DEV, PROD
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = DEV

    @field_validator("environment")
    def environment_values(cls, v):
        if v is None:
            return None
        if v not in [PROD, DEV]:
            raise ValueError(f"Incorrect environment value: {v}")
        return v

    postgres_async_url: str = (
        "postgresql+asyncpg://store_visit:store_visit@127.0.0.1:5432/store_visit"
    )
    postgres_url: str = "postgresql://store_visit:store_visit@127.0.0.1:5432/store_visit"
    SQLALCHEMY_DATABASE_URL: str = postgres_url

    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    domain_name: str = "localhost:5000"
    api_path: str = "/api"

    access_token_expire_minutes: int = 360
    refresh_token_expire_minutes: int = (
        60 * 24 * 30
    )  # 60 minutes * 24 hours * 90 days = 30 days
    access_token_secret_key: str = 'iqjwof'
    refresh_token_secret_key: str = 'kqkwjfoi'

    redis_host: str = 'lkewjfiowe'
    redis_port: int = 6379

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://local.dockertoolbox.tiangolo.com"]'
    backend_cors_origins: List[str] = ["*"]

    @field_validator("backend_cors_origins")
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    project_name: str = "StoreVisit"
    default_pagination_limit: int = 20

    async_pool_size: int = 20
    async_max_overflow: int = 10
    async_pool_recycle: int = -1

    sync_pool_size: int = 5
    sync_max_overflow: int = 0
    sync_pool_recycle: int = -1


settings = Settings()

logging_conf = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "{name} {levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "console"},
    },
    "loggers": {
        "": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "handlers": [
                "console",
            ],
            "propagate": True,
        }
    },
}
