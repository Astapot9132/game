import os
from urllib.parse import quote_plus

import dotenv
import colorama
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from cfg import PROD
from logger import GLOG

colorama.just_fix_windows_console()

dotenv.load_dotenv()



DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_DRIVER = os.getenv('DB_DRIVER', 'mysql+aiomysql')
DB_QUERY = os.getenv('DB_QUERY', 'charset=utf8mb4')


DB_ADMIN_USER = quote_plus(os.getenv('DB_ADMIN_USER', 'root'))
DB_ADMIN_PASSWORD = quote_plus(os.getenv('DB_ADMIN_PASSWORD', 'pass'))

ADB_URL = f"{DB_DRIVER}://{DB_ADMIN_USER}:{DB_ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_QUERY}"
ADB_ENGINE = create_async_engine(
    ADB_URL,
    echo=not PROD,
    pool_pre_ping=True,
)
# admin_session = async_sessionmaker(ADB_ENGINE, class_=AsyncSession, expire_on_commit=False)

DB_SCRIPT_USER = quote_plus(os.getenv('DB_SCRIPT_USER', 'script'))
DB_SCRIPT_PASSWORD = quote_plus(os.getenv('DB_SCRIPT_PASSWORD', 'pass'))

SDB_URL = f"{DB_DRIVER}://{DB_SCRIPT_USER}:{DB_SCRIPT_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?{DB_QUERY}"
SDB_ENGINE = create_async_engine(
    SDB_URL,
    echo=not PROD,
    pool_pre_ping=True,
)
# script_session = async_sessionmaker(SDB_ENGINE, class_=AsyncSession, expire_on_commit=False)
# 
# 
# async def get_admin_session():
#     async with admin_session() as session:
#         yield session
#         
# async def get_script_session():
#     async with script_session() as session:
#         yield session
