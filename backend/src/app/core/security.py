from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.src.infrastructure.repositories.user_repository import UserRepository
from cfg import JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    payload = {'user_id': user_id, 'exp': expire}
    return jwt.encode(payload, JWT_SECRET)


def create_access_token(user_id: int) -> str:
    return _create_token(user_id, int(ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, int(REFRESH_TOKEN_EXPIRE_MINUTES))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repo: UserRepository,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Ошибка авторизации',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id: Optional[int] = payload.get('user_id')
    except JWTError as exc:
        raise credentials_exception from exc

    if user_id is None:
        raise credentials_exception

    user = await repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user