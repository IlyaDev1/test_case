from pathlib import Path

from dishka import Provider, Scope, provide

from src.core.application.skill.registry_service import SkillRegistryService
from src.infra.protocol.docx_exporter import DocxProtocolExporterService
from src.infra.skill.filesystem_repo import FilesystemSkillRepo

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SKILLS_DIR = PROJECT_ROOT / "skills"


class InfraProvider(Provider):
    scope = Scope.APP

    @provide
    def skills_dir(self) -> Path:
        return SKILLS_DIR

    docx_exporter = provide(DocxProtocolExporterService)
    filesystem_skill_repo = provide(FilesystemSkillRepo)

    @provide
    def skill_registry_service(
        self,
        skills_dir: Path,
        filesystem_skill_repo: FilesystemSkillRepo,
    ) -> SkillRegistryService:
        registry = SkillRegistryService(skills_dir, loader=filesystem_skill_repo)
        registry.load()
        return registry
