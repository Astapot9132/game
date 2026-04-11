from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork
from src.app.core.services.security import SecurityService
from fastapi import Request

async def api_script_uow():
    uow = container.script_uow()
    async with uow:
        yield uow

def require_auth(request: Request):
    return container.security_service().require_auth(request)

class Container(containers.DeclarativeContainer):

    admin_engine = providers.Singleton(
        create_async_engine,
        isolation_level='READ COMMITTED',
        url=ADB_URL,
        # echo=True,
        pool_pre_ping=True,
    )

    script_engine = providers.Singleton(
        create_async_engine,
        isolation_level='READ COMMITTED',
        url=SDB_URL,
        # echo=True,
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
    
    admin_session = providers.Factory(admin_sessionmaker())
    script_session = providers.Factory(script_sessionmaker())

    admin_uow = providers.Factory(
        UnitOfWork, session=admin_session
    )
    script_uow = providers.Factory(
        UnitOfWork, session=script_session
    )

    security_service = providers.Singleton(
        SecurityService,
    )


container = Container()

