from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from api.depends import get_session
from exceptions import AlreadyExistsException, DataValidationException
from schemas.user_schemas import UserOut, UserIn, User, UserFilter
from usecases.crm_usecases import create_user_usecase, get_users_usecase

router = APIRouter()


@router.post(
    '/create-user/',
    status_code=status.HTTP_201_CREATED,
    description='Create user, only admin',
    response_model=UserOut
)
async def create_user(
        user_in: UserIn,
        db_session: Session = Depends(get_session),
        # user_phone: str = Depends(get_current_user),
):
    user = User(**user_in.model_dump(exclude_unset=True))

    try:
        return await create_user_usecase(db_session, user, user_in.password)
    except AlreadyExistsException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )


@router.get(
    "/get-users/",
    status_code=status.HTTP_200_OK,
    description="List users with filter(first_name, username)",
    response_model=List[UserOut]
)
async def get_userss(
        filters: UserFilter = Depends(),
        db_session: Session = Depends(get_session)
):
    try:
        return await get_users_usecase(db_session, filters)
    except DataValidationException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': e.message, 'error_code': e.error_code},
        )
