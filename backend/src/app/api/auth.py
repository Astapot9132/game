from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.di_container import container
from backend.src.app.core.security import verify_password, create_access_token, create_refresh_token
from backend.src.app.pydantic_models.auth import TokenAuthResponse, LoginScheme
from backend.src.infrastructure.repositories.user_repository import UserRepository
from backend.src.modules.shared.unit_of_work import UnitOfWork

auth_router = APIRouter(prefix="/auth")



@auth_router.post('/login', response_model=TokenAuthResponse)
async def login(data: LoginScheme, uow: UnitOfWork = Depends(container.script_uow)):
    user = await uow.user_repository.get_by_login(data.login)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Ошибка авторизации')

    return {
        'access_token': create_access_token(user.id),
        'refresh_token': create_refresh_token(user.id),
        'token_type': 'Bearer',
    }