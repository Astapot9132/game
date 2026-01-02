from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG


@providers.Factory
@asynccontextmanager
async def script_session():
    session_maker = container.script_sessionmaker()
    async with session_maker() as session:
        yield session
    GLOG.info('закрыли скрипт')


@providers.Factory
@asynccontextmanager
async def admin_session():
    session_maker = container.admin_sessionmaker()
    async with session_maker() as session:
        yield session
    GLOG.info('закрыли админ')


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.app.api.auth"])

    admin_engine = providers.Singleton(
        create_async_engine,
        url=ADB_URL,
        echo=True,
        pool_pre_ping=True
    )

    script_engine = providers.Singleton(
        create_async_engine,
        url=SDB_URL,
        echo=True,
        pool_pre_ping=True
    )

    admin_sessionmaker = providers.Factory(
        async_sessionmaker,
        bind=admin_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    script_sessionmaker = providers.Factory(
        async_sessionmaker,
        bind=script_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    admin_uow = providers.Factory(UnitOfWork, session=admin_session.provider)
    script_uow = providers.Factory(UnitOfWork, session=admin_session.provider)





container = Container()