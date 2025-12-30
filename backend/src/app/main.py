from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.src.app.api.auth import auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="Battle Cards Arena",)
    app.include_router(auth_router)
    
    return app


app = create_app()



@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


