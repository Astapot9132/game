from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide
from fastapi import FastAPI, Depends

from backend.di_container import container, Container
from backend.src.app.api.auth import auth_router
from backend.src.modules.shared.unit_of_work import UnitOfWork
from logger import GLOG


@asynccontextmanager
async def lifespan(app: FastAPI):
    container.wire(modules=["backend.src.app.api.auth"])
    GLOG.info("Контейнер настроен (wire)")

    yield

    container.unwire()

def create_app() -> FastAPI:
    app = FastAPI(title="Battle Cards Arena", lifespan=lifespan)
    app.include_router(auth_router)
    
    return app


app = create_app()



@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


