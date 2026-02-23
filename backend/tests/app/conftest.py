import sys
from contextlib import asynccontextmanager

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport
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
@pytest_asyncio.fixture
async def client(test_app: FastAPI):
    transport = ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def test_uow():
    uow = container.script_uow()
    async with uow:
        yield uow