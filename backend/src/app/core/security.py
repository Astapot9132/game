from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated, Optional, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from passlib.exc import InvalidTokenError

from backend.di_container import api_script_uow
from backend.src.app.pydantic_models.auth import JWTScheme
from backend.src.infrastructure.repositories.user_repository import UserRepository
from backend.cfg import JWT_SECRET, ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS
from backend.src.modules.shared.unit_of_work import UnitOfWork

pwd_context = CryptContext(schemes=['bcrypt'],
                           bcrypt__default_rounds=12,
                           bcrypt__ident='2b'
                           )
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def _create_token(user_id: int, expires_delta: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    payload = {'user_id': user_id, 'exp': expire}
    return jwt.encode(payload, JWT_SECRET)

def create_access_token(user_id: int) -> str:
    return _create_token(user_id, ACCESS_TOKEN_EXPIRE_SECONDS)

def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, REFRESH_TOKEN_EXPIRE_SECONDS)

def decode_refresh_token(token) -> JWTScheme:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return JWTScheme(**payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token expired"})
    except (InvalidTokenError, JWTError):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})
    except ValueError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})



async def get_current_user(
    request: Request,
    uow: UnitOfWork
):
    access_token = request.cookies.get('access_token')
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Ошибка авторизации',
    )
    if not access_token:
        raise credentials_exception

    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=['HS256'])
        user_id: Optional[int] = payload.get('user_id')
    except JWTError as exc:
        raise credentials_exception from exc

    if user_id is None:
        raise credentials_exception

    user = await uow.user_repository.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user