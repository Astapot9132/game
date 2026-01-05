from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork

async def api_script_uow():
    uow = container.script_uow()
    async with uow:
        yield uow


class Container(containers.DeclarativeContainer):

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
    
    admin_session = providers.Factory(admin_sessionmaker())
    script_session = providers.Factory(script_sessionmaker())

    admin_uow = providers.Factory(
        UnitOfWork, session=admin_session
    )
    script_uow = providers.Factory(
        UnitOfWork, session=script_session
    )


container = Container()

