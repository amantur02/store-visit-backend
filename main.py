from logging.config import dictConfig

from api.api import api_router
from core.config import logging_conf, settings
from core.constants import PROD
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from middlewares import add_process_time_header
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from exceptions import StoreVisitHTTPException

dictConfig(logging_conf)

openapi_url = (
    f"{settings.api_v1_path}/openapi.json"
    if settings.environment != PROD
    else ""
)


app = FastAPI(title=settings.project_name, openapi_url=openapi_url)


app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(api_router, prefix=settings.api_v1_path)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)


@app.exception_handler(StoreVisitHTTPException)
async def bank_exception_handler(_: Request, exc: StoreVisitHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "error_code": exc.error_code},
    )


if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.project_name,
        version="1.0.0",
        description="Sore Visit API",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": 'Enter: **"Bearer &lt;JWT&gt;"**, where JWT is the access token',
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
