from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from backend.db_connection import ADB_URL, SDB_URL
from backend.src.modules.shared.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["backend.src.app.api.auth"])

    # admin_sessionmaker = providers.Singleton(
    #     async_sessionmaker, bind=ADB_ENGINE, class_=AsyncSession, expire_on_commit=False
    # )
    # script_sessionmaker = providers.Singleton(
    #     async_sessionmaker, bind=SDB_ENGINE, class_=AsyncSession, expire_on_commit=False
    # )

    # admin_session = providers.Resource(
    #     async_sessionmaker, bind=ADB_ENGINE, class_=AsyncSession, expire_on_commit=False
    # )
    # script_session = providers.Resource(
    #     async_sessionmaker, bind=SDB_ENGINE, class_=AsyncSession, expire_on_commit=False
    # )

    # Фабрики для создания engine
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
    
    # Ресурсы для сессий
    admin_session = providers.Resource(admin_sessionmaker)
    script_session = providers.Resource(script_sessionmaker)

    admin_uow = providers.Factory(UnitOfWork, session=admin_session)
    script_uow = providers.Factory(UnitOfWork, session=script_session)





container = Container()