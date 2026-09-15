from fastapi import FastAPI

from src.presentation.fastapi.health.router import health_router
from src.presentation.fastapi.protocol.router import protocol_router
from src.presentation.fastapi.skills.router import skills_router


def create_app() -> FastAPI:
    app = FastAPI(title="LLM Skills")
    app.include_router(health_router)
    app.include_router(skills_router)
    app.include_router(protocol_router)
    return app
