from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import AsyncContainer
from fastapi import FastAPI

from src.core.application.skill.registry_service import SkillRegistryService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container: AsyncContainer = app.state.dishka_container
    async with container() as request_container:
        registry = await request_container.get(SkillRegistryService)
        registry.load()

    yield

    await container.close()
