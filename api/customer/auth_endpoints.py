from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session
from exceptions import NotFoundException, AuthenticationError
from schemas.auth_schemas import TokenSchema
from schemas.user_schemas import UserLoginIn
from usecases.customer_usecases import user_login_usecase

router = APIRouter()


@router.post(
    '/login/',
    status_code=status.HTTP_200_OK,
    description='Customer login',
    response_model=TokenSchema,
)
async def customer_login(
    user_in: UserLoginIn,
    db_session: Session = Depends(get_session),
):
    try:
        return await user_login_usecase(
            db_session,
            username=user_in.username,
            password=user_in.password,
        )
    except NotFoundException as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": e.message, "error_code": e.error_code},
        )
    except AuthenticationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": e.message, "error_code": e.error_code},
        )
