import sys
from contextlib import asynccontextmanager
import pytest
import pytest_asyncio
from fastapi import FastAPI
from starlette.testclient import TestClient

from backend.di_container import container
from backend.src.app.api.auth import auth_router
from backend.logger import GLOG


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    # container.wire(modules=["backend.src.app.api.auth"])
    GLOG.info("Контейнер настроен в тестовом режиме (wire)")

    yield

    # container.unwire()
    GLOG.info("Контейнер отключён (unwire)")

@pytest.fixture
def test_app():

    app = FastAPI(lifespan=test_lifespan)

    app.include_router(auth_router)

    return app


# TestClient
@pytest.fixture
def client(test_app: FastAPI):
    with TestClient(test_app) as client:
        yield client


@pytest_asyncio.fixture(scope='function')
async def test_uow():
    uow = container.script_uow()
    async with uow:
        yield uow