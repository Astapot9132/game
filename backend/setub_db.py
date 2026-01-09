import asyncio
import os
from pathlib import Path
from urllib.parse import quote_plus

import dotenv
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.ext.asyncio import create_async_engine

from backend.db_connection import DB_NAME, DB_SCRIPT_USER, DB_SCRIPT_PASSWORD
from backend.cfg import PROD
from logger import GLOG

dotenv.load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
ALEMBIC_INI = BASE_DIR / "src" / "alembic.ini"

DB_DRIVER = os.getenv("DB_DRIVER", "mysql+aiomysql")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_QUERY = os.getenv("DB_QUERY", "charset=utf8mb4")
DB_ADMIN_USER = quote_plus(os.getenv('DB_ADMIN_USER'))
DB_ADMIN_PASSWORD = quote_plus(os.getenv('DB_ADMIN_PASSWORD'))
DB_URL = f"{DB_DRIVER}://{DB_ADMIN_USER}:{DB_ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}?{DB_QUERY}"
DB_ENGINE = create_async_engine(
    DB_URL,
    echo=not PROD,
    pool_pre_ping=True,
    isolation_level='AUTOCOMMIT',
)

async def create_db():
    query = text(f"CREATE DATABASE {DB_NAME};")
    async with DB_ENGINE.connect() as sql_conn:

        try:
            await sql_conn.execute(query)
            GLOG.info(f"База данных '{DB_NAME}' создана успешно")
        except ProgrammingError:
            GLOG.info(f"База данных '{DB_NAME}' уже существует")
        except Exception as e:
            GLOG.info(f'Произошла ошибка: {e}')
        
    await DB_ENGINE.dispose()
    
async def create_user(login: str, password: str):
    query = text(f"""
      CREATE USER '{login}'@'localhost' IDENTIFIED BY '{password}';
      GRANT ALL PRIVILEGES ON game.* TO '{login}'@'%';
      FLUSH PRIVILEGES;
    """)
    async with DB_ENGINE.connect() as sql_conn:
        try:
            await sql_conn.execute(query)
            GLOG.info(f"Пользователь '{login}' создан успешно")
        except OperationalError:
            GLOG.info(f"Пользователь '{login}' уже существует")
    await DB_ENGINE.dispose()

async def main():

    await create_db()
    await create_user(login=DB_SCRIPT_USER, password=DB_SCRIPT_PASSWORD)


if __name__ == "__main__":
    asyncio.run(main())