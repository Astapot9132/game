import asyncio
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, quote_plus


import dotenv
import sqlalchemy
from alembic import command
from alembic.config import Config
from sqlalchemy import select, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADMIN_USER, ADMIN_PASSWORD, SCRIPT_USER, SCRIPT_PASSWORD, DB_NAME, admin_session, \
    ADB_ENGINE
from backend.db_mixins import DBUserTypeEnum
from backend.src.app.core.security import hash_password
from backend.src.infrastructure.enums.users.enums import UserTypeEnum
from backend.src.infrastructure.models.users import User
from cfg import PROD
from logger import GLOG

dotenv.load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_INI = BASE_DIR / "src" / "alembic.ini"

# DB_DRIVER = os.getenv("DB_DRIVER", "mysql+aiomysql")
# DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
# DB_PORT = os.getenv("DB_PORT", "3306")
# DB_NAME = os.getenv("DB_NAME")
# DB_QUERY = os.getenv("DB_QUERY", "charset=utf8mb4")
# ADMIN_DB_USER = os.getenv("ADMIN_USER", "root")
# ADMIN_DB_PASSWORD = os.getenv("ADMIN_PASSWORD", "pass")
# SCRIPT_DB_USER = os.getenv("SCRIPT_USER", ADMIN_DB_USER)
# SCRIPT_DB_PASSWORD = os.getenv("SCRIPT_PASSWORD", ADMIN_DB_PASSWORD)
#

async def create_db():
    query = text(f"CREATE DATABASE {DB_NAME};")
    async with ADB_ENGINE.connect() as sql_conn:
        # Устанавливаем autocommit для этого соединения
        await sql_conn.execution_options(skip_autocommit_rollback=True)

        try:
            await sql_conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            GLOG.info(f"База данных '{DB_NAME}' создана или уже существует")
        except ProgrammingError:
            GLOG.info(f"База данных '{DB_NAME}' уже существует")
        finally:
            await sql_conn.close()


async def main():
    users = [
        (ADMIN_USER, ADMIN_PASSWORD),
        (SCRIPT_USER, SCRIPT_PASSWORD)
    ]
    await create_db()


if __name__ == "__main__":
    asyncio.run(main())