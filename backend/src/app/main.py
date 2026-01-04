from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.di_container import container
from backend.src.app.api.auth import auth_router
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


