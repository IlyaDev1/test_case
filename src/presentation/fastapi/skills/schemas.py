from pydantic import BaseModel


class SkillMetaResponse(BaseModel):
    name: str
    caption: str
    description: str
    has_files: bool
