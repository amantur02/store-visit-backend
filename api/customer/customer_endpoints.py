from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session, get_current_user, get_current_customer
from exceptions import NotFoundException, DataValidationException, AccessDeniedException
from schemas.auth_schemas import SuccessResponse
from schemas.order_schemas import OrderOut, OrderIn, Order, OrderFilter, OrderUpdateIn, StoreOut, StoreFilter, VisitOut, \
    VisitIn, Visit
from schemas.user_schemas import User
from usecases.customer_usecases import create_order_usecase, get_orders_usecase, update_order_usecase, \
    delete_order_usecase, get_stores_usecase, create_visit_usecase

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


@router.patch(
    "/orders/{order_id}/",
    status_code=status.HTTP_200_OK,
    description="Update order",
    response_model=OrderOut,
)
async def update_order(
        order_id: int,
        order_in: OrderUpdateIn,
        db_session: Session = Depends(get_session)
):
    order = Order(**order_in.model_dump(exclude_unset=True))
    order.id = order_id
    try:
        return await update_order_usecase(db_session, order)
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': e.message, 'error_code': e.error_code}
        )


@router.delete(
    "/order/{order_id}/",
    status_code=status.HTTP_200_OK,
    description="Delete order",
    response_model=SuccessResponse,
)
async def delete_order(
        order_id: int,
        db_session: Session = Depends(get_session)
):
    try:
        await delete_order_usecase(db_session, order_id)
        return SuccessResponse(message=f"Order with id {order_id} deleted")
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )


@router.get(
    "/stores/",
    status_code=status.HTTP_200_OK,
    description="List store with filter id and title",
    response_model=List[StoreOut],
)
async def get_stores(
        filters: StoreFilter = Depends(),
        db_session: Session = Depends(get_session),
):
    try:
        return await get_stores_usecase(db_session, filters)
    except DataValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )


@router.post(
    "/create-visit/",
    status_code=status.HTTP_201_CREATED,
    description="Create visit only customer",
    dependencies=[Depends(get_current_customer)],
    response_model=VisitOut
)
async def create_visit(
        visit_in: VisitIn,
        db_session: Session = Depends(get_session),
        user: User = Depends(get_current_user),
):
    visit = Visit(**visit_in.model_dump(exclude_unset=True))
    visit.customer_id = user.id
    try:
        return await create_visit_usecase(db_session, user, visit)
    except AccessDeniedException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )
    except DataValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )

