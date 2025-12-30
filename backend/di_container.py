from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from backend.db_connection import ADB_ENGINE, SDB_ENGINE
from backend.src.modules.shared.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.api.auth"])

    admin_sessionmaker = providers.Singleton(
        async_sessionmaker(ADB_ENGINE, class_=AsyncSession, expire_on_commit=False)
    )
    script_sessionmaker = providers.Singleton(
        async_sessionmaker(SDB_ENGINE, class_=AsyncSession, expire_on_commit=False)
    )
    
    admin_uow = providers.Factory(UnitOfWork, session=admin_sessionmaker())
    script_uow = providers.Factory(UnitOfWork, session=script_sessionmaker())
    
    
    
    

container = Container()