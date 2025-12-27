# Snippet Dropzone

Используй файл как буфер для кода: сначала строка с путём файла, затем блок текста с содержимым. Пример:

```
backend/app/example.py
# код здесь
```

Ниже держи только актуальные сниппеты — старое можно удалять после использования.

## Sessionmaker в cfg.py
- Расширь конфиг переменными `DB_NAME`, `DB_DRIVER` (например `mysql+aiomysql`) и собери DSN в одном месте, чтобы его переиспользовать в любом модуле.
- Создай `create_async_engine` и `async_sessionmaker` прямо в `cfg.py` (или экспортируй функцию, которая их строит), чтобы FastAPI зависимостям оставалось вызвать `get_session`.
- `pool_pre_ping=True` и `expire_on_commit=False` спасают от отвалившихся соединений и позволяют повторно читать объекты после коммита.

cfg.py
```
import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'game_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'changeme')
DB_NAME = os.getenv('DB_NAME', 'game')
DB_DRIVER = os.getenv('DB_DRIVER', 'mysql+aiomysql')
DB_QUERY = os.getenv('DB_QUERY', 'charset=utf8mb4')

user = quote_plus(DB_USER)
password = quote_plus(DB_PASSWORD)
creds = f"{user}:{password}@" if user or password else ''
ASYNC_DATABASE_URL = f"{DB_DRIVER}://{creds}{DB_HOST}:{DB_PORT}/{DB_NAME}"
if DB_QUERY:
    ASYNC_DATABASE_URL = f"{ASYNC_DATABASE_URL}?{DB_QUERY}"

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=not PROD,
    pool_pre_ping=True,
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session_maker() as session:
        yield session
```

## JWT-авторизация во FastAPI
1. Сделай файл `backend/app/core/security.py`, где будут функции для хэширования паролей, генерации/проверки JWT и зависимость `get_current_user`.
2. Используй `passlib.context.CryptContext` для `bcrypt`, библиотеку `python-jose` для токенов и `OAuth2PasswordBearer` как dependency.
3. Логика логина:
   - найти пользователя по e-mail/юзернейму;
   - проверить пароль через `verify_password`;
   - выдать пару токенов (`access`, `refresh`) с разным сроком жизни;
   - сохранить refresh (в БД или redis) — опционально, но хорошо бы иметь.
4. Защита эндпоинтов: зависимость `Depends(get_current_user)` парсит токен из заголовка `Authorization: Bearer ...`, проверяет подпись и грузит пользователя.

backend/app/core/security.py
```
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from cfg import JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from backend.app.db.repositories.users import UserRepository

ALGORITHM = 'HS256'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(subject: str, expires_delta: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    payload = {'sub': subject, 'exp': expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(subject, int(ACCESS_TOKEN_EXPIRE_MINUTES or 15))


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, int(REFRESH_TOKEN_EXPIRE_MINUTES or 60 * 24 * 14))


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repo: Annotated[UserRepository, Depends(UserRepository)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        subject: Optional[str] = payload.get('sub')
    except JWTError as exc:
        raise credentials_exception from exc

    if subject is None:
        raise credentials_exception

    user = await repo.get_by_id(subject)
    if user is None:
        raise credentials_exception

    return user
```

backend/app/api/routes/auth.py
```
@router.post('/login', response_model=TokenPair)
async def login(data: LoginSchema, repo: UserRepository = Depends()):
    user = await repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail='Invalid credentials')

    return {
        'access_token': create_access_token(str(user.id)),
        'refresh_token': create_refresh_token(str(user.id)),
        'token_type': 'bearer',
    }
```

Заменяй `UserRepository` и схемы на свои конкретные реализации — важен сам процесс: хэш хранения, выдача токенов и зависимость, которая валидирует `sub` и достаёт пользователя.
