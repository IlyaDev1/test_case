from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.core.application.skill.services import SkillRegistryService

skills_router = APIRouter(
    prefix="/skills",
    tags=["skills"],
    route_class=DishkaRoute,
)


class SkillMetaResponse(BaseModel):
    name: str
    caption: str
    description: str
    has_files: bool


@skills_router.get("")
def list_skills(
    registry: FromDishka[SkillRegistryService],
    q: str | None = Query(default=None),
) -> list[SkillMetaResponse]:
    return [
        SkillMetaResponse(
            name=skill.name,
            caption=skill.caption,
            description=skill.description,
            has_files=skill.has_files,
        )
        for skill in registry.search(q)
    ]
