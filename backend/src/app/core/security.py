import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated, Optional, Any

import itsdangerous
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from passlib.exc import InvalidTokenError
from pydantic import ValidationError

import secrets
from fastapi import HTTPException, Request, status
from starlette.responses import Response


from backend.di_container import api_script_uow
from backend.src.app.pydantic_models.auth import JWTScheme
from backend.src.infrastructure.repositories.user_repository import UserRepository
from backend.cfg import JWT_SECRET, ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS, CSRF_SECRET
from backend.src.modules.shared.unit_of_work import UnitOfWork
from cfg import REFRESH_TOKEN_PEPPER
from logger import GLOG

pwd_context = CryptContext(schemes=['bcrypt'],
                           bcrypt__default_rounds=12,
                           bcrypt__ident='2b'
                           )
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

CSRF_COOKIE = "csrf_token"
ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"
CSRF_HEADER = "X-CSRF-Token"
CSRF_SERIALIZER = itsdangerous.URLSafeTimedSerializer(CSRF_SECRET)

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

def encode_refresh_token_for_db(token: str):
    digest = hmac.new(
        REFRESH_TOKEN_PEPPER,
        token.encode("utf-8"),
        hashlib.sha256
    ).digest()
    return digest

def decode_token(token, options: dict[str, Any] = None) -> JWTScheme:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options=options)
        return JWTScheme(**payload)
    except ExpiredSignatureError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={"error": "token expired"})
    except (InvalidTokenError, JWTError):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})


def require_auth(request: Request) -> JWTScheme:
    GLOG.info('Проверяем аутентификацию')
    access_token = request.cookies.get(ACCESS_COOKIE)
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not authorized')

    user_payload = decode_token(access_token)
    return user_payload


def require_csrf(request: Request) -> None:
    GLOG.info('Проверяем csrf') # TODO надо вынести логгер в DI
    cookie_token = request.cookies.get(CSRF_COOKIE)
    header_token = request.headers.get(CSRF_HEADER)
    if not cookie_token or not header_token:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token required")
    if not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token mismatch")
    try:
        CSRF_SERIALIZER.loads(cookie_token)
    except itsdangerous.BadSignature:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token invalid")

def set_access_token(response: Response, user_id: int):
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=create_access_token(user_id),
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS, # специально кладем на время рефреш токена, чтобы он не исчез
    )
    
def set_refresh_token(response: Response, user_id: int):
    response.set_cookie(
        key=REFRESH_COOKIE, 
        value=create_refresh_token(user_id), 
        max_age=REFRESH_TOKEN_EXPIRE_SECONDS, 
        httponly=True, 
        path="/auth/refresh"
    )
    
def create_csrf_token() -> str:
    token = CSRF_SERIALIZER.dumps({
        "nonce": secrets.token_urlsafe(16),
      })
    return token

def set_csrf_cookie(response: Response, token):
    response.set_cookie(
      CSRF_COOKIE,
      token,
      httponly=False,
      samesite="strict",
    )



