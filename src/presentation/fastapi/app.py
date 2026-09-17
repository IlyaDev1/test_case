# ruff: noqa: E402
from config.bootstrap import load_runtime_env  # isort: ignore

load_runtime_env()  # isort: ignore

import os

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.infra.di import create_container
from src.presentation.fastapi.health.router import health_router
from src.presentation.fastapi.lifespan import lifespan
from src.presentation.fastapi.protocol.router import protocol_router
from src.presentation.fastapi.skills.router import skills_router


def create_app() -> FastAPI:
    app = FastAPI(title="LLM Skills", lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(skills_router)
    app.include_router(protocol_router)

    container = create_container(with_fastapi=True)
    setup_dishka(container=container, app=app)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="src.presentation.fastapi.app:create_app",
        factory=True,
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=True,
        access_log=False,
        log_level="info",
    )
