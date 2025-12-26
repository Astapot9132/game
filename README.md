# Battle Cards Arena

## Vision
Battle Cards Arena — учебный PvP-проект, где два игрока собирают армии из карточек юнитов на ограниченный бюджет и сражаются раунд за раундом. Цель проекта — прокачать навыки разработки на Vue 3/TypeScript и FastAPI с SQLAlchemy 2, пройдя путь от скелета приложения до production-ready сервиса с аутентификацией, историей игр и личным кабинетом.

## Core Experience (MVP)
- Регистрация и вход по JWT с refresh-токенами и RBAC (admin/player).
- После логина игрок видит дашборд с балансом, списком активных матчей и кнопкой "Создать битву".
- Матч создаёт бюджет, игрок покупает юнитов (мечники, копейщики, лучники, кавалерия) и фиксирует состав.
- Сервер рассчитывает исход пошагово: каждый юнит наносит удар, погибшие заменяются следующими в очереди, пока в армии не останется живых бойцов.
- Результаты и логи раундов сохраняются в историю, доступны в разделе профиля.

## Feature Roadmap
- **MVP**: Auth, профиль, CRUD юнитов, создание/участие в битве, запись истории, базовый фронт.
- **Iteration 2**: Matchmaking, friends/invites, настройка правил боя, короткие реплеи.
- **Iteration 3**: Рейтинги, асинхронные уведомления, платёжные механики, аналитика, анти-cheat хуки.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic Settings, JWT через `python-jose`, шифрование паролей `passlib[bcrypt]`.
- **Frontend**: Vue 3 + Vite + TypeScript, Pinia для стора, Vue Router, TailwindCSS (или Naive UI) для UI, Axios/FETCH для API.
- **Data & Infra**: PostgreSQL (основная БД) / SQLite на ранних этапах, Redis или Dragonfly для кэша, Docker Compose для локального окружения, GitHub Actions для CI.
- **Dev Tooling**: Poetry для зависимостей, Ruff/Black/Isort для стиля, pytest + pytest-asyncio, Playwright/Vitest на фронте.

## Repository Layout (план)
```
game/
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── alembic/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
├── frontend/
│   ├── package.json
│   └── src/
└── docs/
    ├── api.md
    └── battle_rules.md
```

## Backend Setup (Poetry + FastAPI)
1. Создай структуру и инициализируй Poetry:
   ```bash
   mkdir -p backend && cd backend
   poetry init --name battle_cards_backend --dependency fastapi --dependency "uvicorn[standard]"
   poetry env use python3.12
   ```
2. Поставь основные пакеты:
   ```bash
   poetry add fastapi uvicorn[standard] pydantic-settings sqlalchemy[asyncio] alembic psycopg[binary] asyncpg passlib[bcrypt] python-jose[cryptography] bcrypt redis
   poetry add --group dev ruff black isort pytest pytest-asyncio httpx
   ```
3. Создай точку входа `app/main.py`:
   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Battle Cards Arena")

   @app.get("/health", tags=["health"])
   async def health_check():
       return {"status": "ok"}
   ```
4. Настрой конфиг через Pydantic Settings (`app/core/config.py`) и `.env`:
   ```env
   APP_ENV=local
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/battle_cards
   REDIS_URL=redis://localhost:6379/0
   JWT_SECRET=change-me
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=4320
   ```
5. Миграции:
   ```bash
   alembic init app/db/migrations
   ```
   В `alembic.ini` поставь SQLAlchemy URL из `.env`, а в `env.py` подключи модель `Base`.
6. Запуск:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Полезные Poetry-команды
- `poetry install` — ставит зависимости из `pyproject.toml` и `poetry.lock`.
- `poetry run pytest` — запускает тесты в виртуальном окружении.
- `poetry shell` — интерактивный shell внутри окружения.
- `poetry export -f requirements.txt --output requirements.txt` — если нужно requirements для CI/CD.

## Frontend Setup (Vue 3 + Vite)
1. Создай приложение:
   ```bash
   mkdir -p frontend && cd frontend
   npm create vite@latest . -- --template vue-ts
   npm install
   npm install pinia vue-router axios tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```
2. Настрой `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```
3. Создай базовый клиент API `src/lib/api.ts`:
   ```ts
   import axios from 'axios';

   export const api = axios.create({
     baseURL: import.meta.env.VITE_API_BASE_URL,
     withCredentials: false,
   });
   ```
4. Добавь маршруты (`/login`, `/register`, `/dashboard`, `/history`) и Pinia store для auth (хранение access/refresh токенов и пользователя).
5. Запуск:
   ```bash
   npm run dev
   ```

## Database Decision Guide
| Опция       | Когда использовать                                  | Плюсы                                                         | Минусы |
|-------------|------------------------------------------------------|---------------------------------------------------------------|--------|
| PostgreSQL  | Основная целевая БД и когда нужна надёжность         | Богатые типы данных, JSONB, расширения, хорошая документация | Требует сервера/контейнера, чуть сложнее разворачивать |
| SQLite      | Быстрый прототип, локальные тесты/CI                | Zero-config, файл в репо, миграции через Alembic работают     | Нет параллелизма, ограниченные типы, блокировки |
| MySQL/MariaDB| Для расширения кругозора и совместимости           | Популярна, много хостингов                                  | Нужно учитывать `autocommit`, отличия типов чисел |
| CockroachDB/Neon | Когда хочется попробовать горизонтальное масштабирование | Совместима с PostgreSQL драйверами, serverless режим          | Молодые платформы, возможны ограничения/квоты |

Рекомендация: начинать с PostgreSQL (если уже разворачиваешь контейнер) или SQLite (если хочешь стартовать моментально). Переключение на Postgres через SQLAlchemy делается заменой `DATABASE_URL` и перегенерацией миграций.

## Cache Layer Options
- **Redis** — стандарт де-факто: поддержка кластеров, модулей (RedisJSON, Bloom). Для локального режима достаточно `docker run redis`.
- **Dragonfly** — совместим с протоколом Redis, использует все ядра и экономит память. Хорош, если нужен высокий QPS на одной машине. Минус — более молодая экосистема и отсутствие модулей.
- **In-memory TTLCache** — можно временно использовать внутри FastAPI для rate limit или хранения сессий, но данные пропадут при рестарте.
- **KeyDB/Dragonfly** — альтернативы, если хочешь изучить другие модели многопоточности (KeyDB с актив-актив, Dragonfly с lock-free структурами).

## API Draft (первый слой)
- `POST /auth/register` — создание пользователя.
- `POST /auth/login` — выдача пары access/refresh.
- `POST /auth/refresh` — обновление access токена.
- `GET /users/me` — профиль и статистика.
- `GET /units` + `POST /units` — справочник войск (admin-only на создание).
- `POST /battles` — создание комнаты/битвы.
- `POST /battles/{id}/join` — вход второго игрока.
- `POST /battles/{id}/lock` — фиксация состава армии.
- `GET /battles/{id}` — состояние боя + раунды.
- `GET /history` — список завершённых игр пользователя.

## Observability & QA
- Логирование через `structlog` или standard logging + JSON formatter.
- Metrics: Prometheus FastAPI middleware (latency, error rate) + Grafana (позже).
- Tests: unit (сервисы), integration (FastAPI TestClient + SQLite in-memory), e2e (Playwright для фронта).

## Questions To Clarify Next
1. Какая механика подбора соперника: ручные комнаты по коду, авто-матчмейкинг или друзья?
2. Нужно ли хранить подробные логи каждого удара или достаточно итогов раундов?
3. Как считать баланс: фиксированная валюта на аккаунт или выдаётся перед каждой битвой?
4. Планируется ли система редких карточек, апгрейдов, прогрессии?
5. Нужно ли real-time (WebSocket/Server-Sent Events) или асинхронные матчи с периодическими обновлениями достаточны?
6. Какие политики retention для истории боёв и логов?

## Next Steps
1. Произведи scaffold backend/frontend по шагам выше.
2. Реши, запускаешь ли PostgreSQL (docker-compose) или начинаешь с SQLite.
3. Определи контракт боя и сохранение истории (`docs/battle_rules.md`).
4. Реализуй вертикальный срез: регистрация → логин → защищённый `/users/me` → отображение на фронте.
5. Настрой базовые тесты и линтеры в CI, чтобы не откладывать на потом.
