from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="url-shortener",
    version="0.1.0",
    description="HTTP skeleton for a URL shortening service.",
)

app.include_router(router)
