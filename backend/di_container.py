from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.di_providers import ScopedResource
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG



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
    
    admin_session = ScopedResource(providers.Callable(lambda sm: sm(), admin_sessionmaker.provider) )
    script_session = ScopedResource(providers.Callable(lambda sm: sm(), script_sessionmaker.provider) )

    admin_uow = providers.Factory(
        UnitOfWork, session=admin_session
    )
    script_uow = providers.Factory(
        UnitOfWork, session=script_session
    )


container = Container()
