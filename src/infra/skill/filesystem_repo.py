import logging
from pathlib import Path

import yaml

from src.core.application.skill.ports import SkillSourcePort
from src.core.domain.skill.entities import SkillMeta
from src.core.domain.skill.exceptions import SkillValidationError

logger = logging.getLogger(__name__)


class FilesystemSkillRepo(SkillSourcePort):
    """Загружает SkillMeta из каталога skills/*/SKILL.md."""

    def __init__(self, skills_dir: Path) -> None:
        self._skills_dir = skills_dir

    def load_all(self) -> tuple[SkillMeta, ...]:
        if not self._skills_dir.is_dir():
            return ()

        skills: list[SkillMeta] = []
        for skill_dir in sorted(self._skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_path = skill_dir / "SKILL.md"
            if not skill_path.is_file():
                continue

            try:
                skills.append(self._load_skill(skill_dir, skill_path))
            except SkillValidationError as exc:
                logger.warning(
                    "Пропуск невалидного скила %s: %s",
                    skill_dir.name,
                    exc.message,
                )
            except Exception as exc:
                logger.warning(
                    "Пропуск скила %s: %s",
                    skill_dir.name,
                    exc,
                )

        return tuple(skills)

    def _load_skill(self, skill_dir: Path, skill_path: Path) -> SkillMeta:
        content = skill_path.read_text(encoding="utf-8")
        frontmatter, body = _parse_frontmatter(content, skill_dir=skill_dir.name)

        name = str(frontmatter.get("name") or skill_dir.name)
        caption = str(frontmatter.get("caption") or "")
        description = str(frontmatter.get("description") or "")

        return SkillMeta.create(
            name=name,
            caption=caption,
            description=description,
            body=body,
            has_files=_has_files(skill_dir),
        )


def _parse_frontmatter(
    content: str,
    *,
    skill_dir: str,
) -> tuple[dict[str, object], str]:
    if not content.startswith("---"):
        raise SkillValidationError(
            "SKILL.md должен начинаться с YAML frontmatter",
            context={"skill_dir": skill_dir},
        )

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise SkillValidationError(
            "некорректный YAML frontmatter",
            context={"skill_dir": skill_dir},
        )

    try:
        raw = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        raise SkillValidationError(
            "ошибка разбора YAML frontmatter",
            context={"skill_dir": skill_dir, "error": str(exc)},
        ) from exc

    if not isinstance(raw, dict):
        raise SkillValidationError(
            "frontmatter должен быть YAML-объектом",
            context={"skill_dir": skill_dir},
        )

    body = parts[2].lstrip("\n")
    return raw, body


def _has_files(skill_dir: Path) -> bool:
    for subdir_name in ("references", "routes"):
        subdir = skill_dir / subdir_name
        if not subdir.is_dir():
            continue
        for path in subdir.rglob("*"):
            if path.is_file():
                return True
    return False
