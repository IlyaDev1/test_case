import threading
from pathlib import Path

from src.core.application.skill.ports import SkillSourcePort
from src.core.domain.skill.entities import SkillMeta


class SkillRegistryService:
    """Потокобезопасный реестр метаданных скилов."""

    def __init__(
        self,
        skills_dir: Path,
        *,
        loader: SkillSourcePort | None = None,
    ) -> None:
        if loader is None:
            from src.infra.skill.filesystem_repo import FilesystemSkillRepo

            loader = FilesystemSkillRepo(skills_dir)
        self._loader = loader
        self._lock = threading.RLock()
        self._snapshot: tuple[SkillMeta, ...] = ()

    def load(self) -> None:
        new_snapshot = self._loader.load_all()
        with self._lock:
            self._snapshot = new_snapshot

    def reload(self) -> None:
        self.load()

    def list_skills(self) -> tuple[SkillMeta, ...]:
        with self._lock:
            return self._snapshot

    def search(self, q: str | None = None) -> tuple[SkillMeta, ...]:
        skills = self.list_skills()
        if q is None or q == "":
            return skills

        needle = q.casefold()
        return tuple(
            skill
            for skill in skills
            if needle in skill.name.casefold() or needle in skill.caption.casefold()
        )
