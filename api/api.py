from api.customer import customer_endpoints as customer_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    customer_router.router, prefix="/customers", tags=["customers"]
)
