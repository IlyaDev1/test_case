from pathlib import Path

from dishka import Provider, Scope, provide

from src.infra.protocol.docx_exporter import DocxProtocolExporterService
from src.infra.skill.filesystem_loader import FilesystemSkillLoader

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SKILLS_DIR = PROJECT_ROOT / "skills"


class InfraProvider(Provider):
    scope = Scope.APP

    @provide
    def skills_dir(self) -> Path:
        return SKILLS_DIR

    docx_exporter = provide(DocxProtocolExporterService)
    filesystem_skill_loader = provide(FilesystemSkillLoader)
