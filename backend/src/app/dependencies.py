from dependency_injector.wiring import Provide
from fastapi import Depends

from backend.di_container import Container
from backend.src.modules.shared.unit_of_work import UnitOfWork


async def start_script_uow(uow: UnitOfWork = Depends(Provide[Container.script_uow])):
    async with uow:
        yield uow
