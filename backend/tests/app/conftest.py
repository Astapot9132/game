import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
import pytest_asyncio
from fastapi import FastAPI
from pyasn1.debug import scope
from starlette.testclient import TestClient

from backend.di_container import container, get_script_uow
from backend.src.app.api.auth import auth_router
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    container.wire(modules=["backend.app.api.auth"])
    GLOG.info("Контейнер настроен в тестовом режиме (wire)")

    yield

    container.unwire()
    GLOG.info("Контейнер отключён (unwire)")

@pytest.fixture
def test_app():

    app = FastAPI(lifespan=test_lifespan)

    app.include_router(auth_router)

    return app


# TestClient
@pytest.fixture
def client(test_app: FastAPI):
    return TestClient(test_app)


@pytest_asyncio.fixture(scope='function')
async def test_uow():
    sm = container.script_sessionmaker()
    async with sm() as session:
        uow = container.script_uow()
        yield uow(session)
# 
# @pytest_asyncio.fixture(scope='function')
# async def test_uow():
#     async with get_script_uow() as uow:
#         yield uow