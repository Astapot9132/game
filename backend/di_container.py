from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG


@asynccontextmanager
async def session_resource(
    session_factory: async_sessionmaker[AsyncSession],
    label: str,
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
        finally:
            GLOG.info("закрыли %s сессию", label)


@asynccontextmanager
async def unit_of_work_resource(
    session_factory: async_sessionmaker[AsyncSession],
    label: str,
) -> AsyncIterator[UnitOfWork]:
    async with session_factory() as session:
        try:
            yield UnitOfWork(session=session)
        finally:
            GLOG.info("закрыли %s UnitOfWork", label)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.app.api.auth"])

    admin_engine = providers.Singleton(
        create_async_engine,
        url=ADB_URL,
        echo=True,
        pool_pre_ping=True,
    )

    script_engine = providers.Singleton(
        create_async_engine,
        url=SDB_URL,
        echo=True,
        pool_pre_ping=True,
    )

    admin_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=admin_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    script_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=script_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    admin_session = providers.Resource(
        session_resource,
        session_factory=admin_sessionmaker,
        label="админ",
    )

    script_session = providers.Resource(
        session_resource,
        session_factory=script_sessionmaker,
        label="скрипт",
    )

    admin_uow = providers.Resource(
        unit_of_work_resource,
        session_factory=admin_sessionmaker,
        label="админ",
    )

    script_uow = providers.Resource(
        unit_of_work_resource,
        session_factory=script_sessionmaker,
        label="скрипт",
    )


container = Container()
