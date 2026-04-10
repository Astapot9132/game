import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Any

import itsdangerous
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from passlib.exc import InvalidTokenError
from pydantic import ValidationError
from starlette.responses import Response

from backend.cfg import JWT_SECRET, ACCESS_TOKEN_EXPIRE_SECONDS, REFRESH_TOKEN_EXPIRE_SECONDS, CSRF_SECRET
from backend.src.app.pydantic_models.auth import JWTScheme
from backend.src.modules.shared.unit_of_work import UnitOfWork
from backend.cfg import REFRESH_TOKEN_PEPPER
from backend.logger import GLOG





class SecurityService:

    PWD_CONTEXT = CryptContext(schemes=['bcrypt'],
                               bcrypt__default_rounds=12,
                               bcrypt__ident='2b'
                               )
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl='auth/login')

    CSRF_COOKIE = "csrf_token"
    ACCESS_COOKIE = "access_token"
    REFRESH_COOKIE = "refresh_token"
    CSRF_HEADER = "X-CSRF-Token"
    CSRF_SERIALIZER = itsdangerous.URLSafeTimedSerializer(CSRF_SECRET)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.PWD_CONTEXT.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def _create_token(cls, user_id: int, expires_delta: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        payload = {'user_id': user_id, 'exp': expire}
        return jwt.encode(payload, JWT_SECRET)

    @classmethod
    def create_access_token(cls, user_id: int) -> str:
        return cls._create_token(user_id, ACCESS_TOKEN_EXPIRE_SECONDS)

    @classmethod
    def create_refresh_token(cls, user_id: int) -> str:
        return cls._create_token(user_id, REFRESH_TOKEN_EXPIRE_SECONDS)

    @classmethod
    def hash_refresh_token_for_db(cls, token: str):
        digest = hmac.new(
            REFRESH_TOKEN_PEPPER,
            token.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return digest

    @classmethod
    def decode_token(cls, token, options: dict[str, Any] = None) -> JWTScheme:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options=options)
            return JWTScheme(**payload)
        except ExpiredSignatureError:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={"error": "token expired"})
        except (InvalidTokenError, JWTError):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})
        except ValidationError:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={"error": "token invalid"})

    @classmethod
    def require_auth(cls, request: Request) -> JWTScheme:
        GLOG.info('Проверяем аутентификацию')
        access_token = request.cookies.get(cls.ACCESS_COOKIE)
        if not access_token:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail='Not authorized')

        user_payload = cls.decode_token(access_token)
        return user_payload


    @classmethod
    def require_csrf(cls, request: Request) -> None:
        GLOG.info('Проверяем csrf') # TODO надо вынести логгер в DI
        cookie_token = request.cookies.get(cls.CSRF_COOKIE)
        header_token = request.headers.get(cls.CSRF_HEADER)
        if not cookie_token or not header_token:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token required")
        if not secrets.compare_digest(cookie_token, header_token):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token mismatch")
        try:
            cls.CSRF_SERIALIZER.loads(cookie_token)
        except itsdangerous.BadSignature:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="CSRF token invalid")

    @classmethod
    def set_access_token(cls, response: Response, user_id: int):
        token = cls.create_access_token(user_id)
        response.set_cookie(
            key=cls.ACCESS_COOKIE,
            value=token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS, # специально кладем на время рефреш токена, чтобы он не исчез
        )
        return token

    @classmethod
    async def set_refresh_token(cls, response: Response, user_id: int, uow: UnitOfWork):
        token = cls.create_refresh_token(user_id)
        await uow.user_repository.update_by_id(id=user_id, values={'refresh_token_hash': cls.hash_refresh_token_for_db(token)})
        response.set_cookie(
            key=cls.REFRESH_COOKIE,
            value=token,
            max_age=REFRESH_TOKEN_EXPIRE_SECONDS,
            httponly=True,
            path="/auth"
        )
        return token

    @classmethod
    def create_csrf_token(cls) -> str:
        token = cls.CSRF_SERIALIZER.dumps({
            "nonce": secrets.token_urlsafe(16),
          })
        return token

    @classmethod
    def set_csrf_cookie(cls, response: Response, token):
        response.set_cookie(
          cls.CSRF_COOKIE,
          token,
          httponly=False,
          samesite="strict",
        )



