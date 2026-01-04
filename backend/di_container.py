from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.di_providers import ScopedResource
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG


async def get_script_uow():
    sm = container.script_sessionmaker()
    async with sm() as session:
        uow = container.script_uow()
        yield uow(session)
    print("Закрыли UOW")


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

    admin_uow = providers.Object(
        UnitOfWork
    )
    script_uow = providers.Object(
        UnitOfWork
    )


container = Container()
