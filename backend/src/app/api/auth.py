from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends, Request
from starlette.responses import JSONResponse

from backend.cfg import ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS
from backend.di_container import api_script_uow
from backend.src.app.core.security import verify_password, create_access_token, create_refresh_token, hash_password, \
    decode_refresh_token, get_current_user
from backend.src.app.pydantic_models.auth import AuthScheme
from backend.src.infrastructure.enums.users.enums import UserTypeEnum
from backend.src.infrastructure.pydantic_models.users import PyUser
from backend.src.modules.shared.unit_of_work import UnitOfWork

auth_router = APIRouter(prefix="/auth")


@auth_router.post('/login')
async def login(data: AuthScheme, uow: UnitOfWork = Depends(api_script_uow)):
    user = await uow.user_repository.get_by_login(data.login)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail='Ошибка авторизации')

    assert user.id

    response = JSONResponse(
        status_code=HTTPStatus.OK, content={}
    )
    response.set_cookie(
        key="access_token",
        value=create_access_token(user.id),
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_SECONDS,
    )
    response.set_cookie(
        key="refresh_token",
        value=create_refresh_token(user.id),
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
        path="/auth/refresh"
    )
    return response

@auth_router.post('/registration')
async def registration(data: AuthScheme, uow: UnitOfWork = Depends(api_script_uow)):
    reg_model = PyUser(
        login=data.login,
        password_hash=hash_password(data.password),
        user_type=UserTypeEnum.player,
        updated_by='Регистрация'
    )
    user_id = await uow.user_repository.add_with_ignore_conflict(
        value=reg_model.model_dump(exclude_unset=True)
    )
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail={"error": 'Пользователь с данным логином уже существует'})

    await uow.commit()
    
    return JSONResponse(status_code=HTTPStatus.OK, content={})


@auth_router.post('/logout')
async def logout():
    response = JSONResponse(status_code=HTTPStatus.OK, content={'request': 'success'})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth/refresh")
    return response

@auth_router.post('/refresh')
async def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "not auth"})
    
    payload = decode_refresh_token(token)
    
    user_id = payload.user_id
    
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    response = JSONResponse(status_code=HTTPStatus.OK, content={})
    response.set_cookie(
        "access_token", value=new_access_token, 
        max_age=ACCESS_TOKEN_EXPIRE_SECONDS, 
        httponly=True,
    )
    response.set_cookie(
        "refresh_token", value=new_refresh_token, 
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS, 
        httponly=True, 
        path="/auth/refresh"
    )
    return response

@auth_router.get('/me')
async def me(request: Request, uow: UnitOfWork = Depends(api_script_uow)):
    user = await get_current_user(request, uow)
    return JSONResponse(status_code=HTTPStatus.OK, content={'id': user.id, 'login': user.login, 'email': user.email})
    