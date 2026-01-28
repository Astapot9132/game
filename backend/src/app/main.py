from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from backend.di_container import container
from backend.src.app.api.auth import auth_router
from logger import GLOG
from src.app.core.security import require_csrf


@asynccontextmanager
async def lifespan(app: FastAPI):
    # container.wire(modules=["backend.src.app.api.auth"])
    GLOG.info("Контейнер настроен (wire)")
    yield
    await container.script_engine().dispose()
    await container.admin_engine().dispose()
    # container.unwire()





app = FastAPI(title="Battle Cards Arena", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


@app.middleware("http")
async def csrf_middleware(request: Request, call_next) -> Response:
    # Проверяем, является ли запрос POST
    if request.method in ("POST", "DELETE", "PUT", "PATCH", ):
        try:
            require_csrf(request)
        except HTTPException as e:
            GLOG.warning(f"CSRF validation failed for {request.url}: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )

    response = await call_next(request)

    return response