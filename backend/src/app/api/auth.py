from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends, Request
from starlette.responses import JSONResponse

from backend.di_container import api_script_uow
from backend.src.app.core.security import verify_password, hash_password, \
    decode_token, set_access_token, set_refresh_token, set_csrf_cookie, require_auth
from backend.src.app.pydantic_models.auth import AuthScheme, JWTScheme
from backend.src.infrastructure.enums.users.enums import UserTypeEnum
from backend.src.infrastructure.pydantic_models.users import PyUser
from backend.src.modules.shared.unit_of_work import UnitOfWork
from src.app.core.security import require_csrf, create_csrf_token, ACCESS_COOKIE, REFRESH_COOKIE, CSRF_COOKIE

auth_router = APIRouter(prefix="/auth",)


@auth_router.post('/login')
async def login(data: AuthScheme, 
                uow: UnitOfWork = Depends(api_script_uow),):
    user = await uow.user_repository.get_by_login(data.login)

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Ошибка авторизации')

    assert user.id

    response = JSONResponse(
        status_code=HTTPStatus.OK, content={}
    )
    set_access_token(response, user.id)
    set_refresh_token(response, user.id)
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
    response.delete_cookie(ACCESS_COOKIE)
    response.delete_cookie(REFRESH_COOKIE, path="/auth/refresh")
    return response

@auth_router.post('/refresh', dependencies=[])
async def refresh(request: Request):
    access_token = request.cookies.get(ACCESS_COOKIE)
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not access_token or not refresh_token:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "not auth"})

    access_payload = decode_token(access_token, options={'verify_exp': False})
    refresh_payload = decode_token(refresh_token, options={'verify_exp': False})
    
    if access_payload.user_id != refresh_payload.user_id:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "not auth"})

    user_id = refresh_payload.user_id

    response = JSONResponse(status_code=HTTPStatus.OK, content={})
    set_access_token(response, user_id)
    set_refresh_token(response, user_id)
    return response

@auth_router.get("/csrf", dependencies=[])
async def csrf():
    token = create_csrf_token()
    response = JSONResponse(content={"csrf_token": token})
    set_csrf_cookie(response, token)
    return response

@auth_router.get('/me', dependencies=[])
async def me(uow: UnitOfWork = Depends(api_script_uow),
             user_payload: JWTScheme = Depends(require_auth)):
    user = await uow.user_repository.get_by_id(user_payload.user_id)
    if user is None:
        raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN,
        detail='Ошибка авторизации',
    )
    return JSONResponse(status_code=HTTPStatus.OK, content={
        'id': user.id, 
        'login': user.login, 
        'email': user.email
    })
    