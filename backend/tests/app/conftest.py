import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

#
# sys.path.append('C:\\Users\\user\\Desktop\\work\\Game')

source_root = Path(__file__).resolve().parent.parent.parent.parent

if str(source_root) not in sys.path:
    sys.path.append(str(source_root))


import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from backend.di_container import container
from backend.src.app.api.auth import auth_router
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
