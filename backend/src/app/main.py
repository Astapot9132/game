from fastapi import FastAPI

app = FastAPI(title="Battle Cards Arena")

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


