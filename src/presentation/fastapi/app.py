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
