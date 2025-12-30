from contextlib import asynccontextmanager

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork


@providers.Factory
@asynccontextmanager
async def script_session():
    session_maker = container.script_sessionmaker()
    async with session_maker() as session:
        yield session
        
@providers.Factory
@asynccontextmanager
async def admin_session():
    session_maker = container.admin_sessionmaker()
    async with session_maker() as session:
        yield session



class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.app.api.auth"])

    admin_engine = providers.Singleton(
        create_async_engine,
        url=ADB_URL,
        echo=True
    )

    script_engine = providers.Singleton(
        create_async_engine,
        url=SDB_URL,
        echo=True
    )

    # Sessionmakers используют engine из фабрик
    admin_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=admin_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    script_sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=script_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    admin_uow = providers.Factory(UnitOfWork, session=admin_session)
    script_uow = providers.Factory(UnitOfWork, session=script_session)





container = Container()