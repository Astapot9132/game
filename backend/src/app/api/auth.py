import asyncio
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends, Response
from starlette.responses import JSONResponse

from backend.di_container import api_script_uow
from backend.src.app.core.security import verify_password, create_access_token, create_refresh_token, hash_password
from backend.src.app.pydantic_models.auth import TokenAuthResponse, AuthScheme
from backend.src.infrastructure.enums.users.enums import UserTypeEnum
from backend.src.infrastructure.models import User
from backend.src.infrastructure.pydantic_models.users import PyUser
from backend.src.modules.shared.unit_of_work import UnitOfWork

auth_router = APIRouter(prefix="/auth")


@auth_router.get("/health", tags=["health"])
async def health_check(uow: UnitOfWork = Depends(api_script_uow)):
    print(uow.session)
    await asyncio.sleep(5)
    print(uow.session)
    return {"status": "ok"}

@auth_router.post('/login', response_model=TokenAuthResponse)
async def login(data: AuthScheme, uow: UnitOfWork = Depends(api_script_uow)):
    user = await uow.user_repository.get_by_login(data.login)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Ошибка авторизации')

    assert user.id

    return JSONResponse(status_code=HTTPStatus.OK, content={
        'access_token': create_access_token(user.id),
        'refresh_token': create_refresh_token(user.id),
        'token_type': 'Bearer',
    })

@auth_router.post('/registration', response_model=TokenAuthResponse)
async def registration(data: AuthScheme, uow: UnitOfWork = Depends(api_script_uow)):
    reg_model = PyUser(
        login=data.login,
        password_hash=hash_password(data.password),
        user_type=UserTypeEnum.player
    )
    user = await uow.user_repository.add_many_with_ignore_conflict(
        values=[reg_model.model_dump(exclude_unset=True)], returning_fields=[User.id], commit=True
    )
    if not user:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Пользователь с данным логином уже существует')
    
    user_id = user[0].id
    return JSONResponse(status_code=HTTPStatus.OK, content={
        'access_token': create_access_token(user_id),
        'refresh_token': create_refresh_token(user_id),
        'token_type': 'Bearer',
    })