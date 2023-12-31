from api.customer import customer_endpoints as customer_router
from api.customer import auth_endpoints as auth_router
from api.crm import crm_endpoints as crm_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    auth_router.router, prefix="/auth", tags=["authentication"]
)
api_router.include_router(
    customer_router.router, prefix="/customers", tags=["customers"]
)
api_router.include_router(
    crm_router.router, prefix="/crm", tags=["crm"]
)
