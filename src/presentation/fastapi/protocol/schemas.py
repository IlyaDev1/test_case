from pydantic import BaseModel, Field

from src.core.application.protocol import DEFAULT_SKILL_NAME


class ExportProtocolRequest(BaseModel):
    text: str


class GenerateProtocolRequest(BaseModel):
    notes: str
    skill_name: str = Field(default=DEFAULT_SKILL_NAME)
