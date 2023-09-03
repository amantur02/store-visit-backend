from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session, get_current_user, get_current_customer
from exceptions import NotFoundException, DataValidationException
from schemas.order_schemas import OrderOut, OrderIn, Order, OrderFilter
from schemas.user_schemas import User
from usecases.customer_usecases import create_order_usecase, get_orders_usecase

router = APIRouter()


@router.post(
    '/create-order/',
    status_code=status.HTTP_201_CREATED,
    description='Create order, only customer',
    response_model=OrderOut,
    dependencies=[Depends(get_current_customer)]
)
async def create_order(
        order_in: OrderIn,
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    order = Order(**order_in.model_dump(exclude_unset=True))

    try:
        return await create_order_usecase(db_session, order, user)
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': e.message, 'error_code': e.error_code},
        )
    except DataValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )


@router.get(
    "/orders/",
    status_code=status.HTTP_200_OK,
    description="Get orders",
    response_model=List[OrderOut],
)
async def get_orders(
        filters: OrderFilter = Depends(),
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user)
):
    try:
        return await get_orders_usecase(db_session, filters, user)
    except DataValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )
