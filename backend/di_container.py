from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.db_connection import ADB_ENGINE, SDB_ENGINE
from backend.src.modules.shared.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.auth"])

    admin_sessionmaker = providers.Singleton(
        async_sessionmaker, bind=ADB_ENGINE, class_=AsyncSession, expire_on_commit=False
    )
    script_sessionmaker = providers.Singleton(
        async_sessionmaker, bind=SDB_ENGINE, class_=AsyncSession, expire_on_commit=False
    )

    admin_session = providers.Resource(
        admin_sessionmaker
    )
    script_session = providers.Resource(
        script_sessionmaker
    )


    admin_uow = providers.Factory(UnitOfWork, session=admin_session)
    script_uow = providers.Factory(UnitOfWork, session=script_session)





container = Container()