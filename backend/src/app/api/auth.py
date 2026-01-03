import asyncio

from dependency_injector.wiring import inject
from fastapi import APIRouter, HTTPException, Depends

from backend.src.app.core.security import verify_password, create_access_token, create_refresh_token
from backend.src.app.dependencies import start_script_uow

from backend.src.app.pydantic_models.auth import TokenAuthResponse, LoginScheme
from backend.src.modules.shared.unit_of_work import UnitOfWork

auth_router = APIRouter(prefix="/auth")

@auth_router.get("/health", tags=["health"])
@inject
async def health_check(uow: UnitOfWork = Depends(start_script_uow)):
    print(f'старт {uow.user_repository.session}')
    await asyncio.sleep(5)
    print(uow.user_repository.session)
    return {"status": "ok"}

@auth_router.post('/login', response_model=TokenAuthResponse)
@inject
async def login(data: LoginScheme, uow: UnitOfWork = Depends(start_script_uow)):
    user = await uow.user_repository.get_by_login(data.login)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Ошибка авторизации')

    return {
        'access_token': create_access_token(user.id),
        'refresh_token': create_refresh_token(user.id),
        'token_type': 'Bearer',
    }
