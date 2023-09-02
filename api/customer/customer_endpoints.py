from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session, get_current_user
from exceptions import NotFoundException
from schemas.order_schemas import OrderOut, OrderIn, Order
from usecases.customer_usecases import create_order_usecase

router = APIRouter()


@router.post(
    '/create-order/',
    status_code=status.HTTP_201_CREATED,
    description='Create order, only customer',
    response_model=OrderOut
)
async def create_order(
        order_in: OrderIn,
        db_session: Session = Depends(get_session),
        user_phone: str = Depends(get_current_user),
):
    order = Order(**order_in.model_dump(exclude_unset=True))

    try:
        return await create_order_usecase(db_session, order)
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': e.message, 'error_code': e.error_code},
        )