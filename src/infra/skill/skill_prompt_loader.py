from pathlib import Path

import yaml

from src.core.application.skill.exceptions import SkillNotFoundError
from src.core.application.skill.skill_prompt_port import SkillPromptPort
from src.core.domain.skill.exceptions import SkillValidationError


class FilesystemSkillPromptLoader(SkillPromptPort):
    """Собирает system prompt из SKILL.md и подфайлов references/ и routes/."""

    def __init__(self, skills_dir: Path) -> None:
        self._skills_dir = skills_dir

    def load(self, skill_name: str) -> str:
        skill_dir = self._skills_dir / skill_name
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            raise SkillNotFoundError(
                f"скил «{skill_name}» не найден",
                context={"skill_name": skill_name},
            )

        content = skill_path.read_text(encoding="utf-8")
        _, body = _parse_frontmatter(content, skill_dir=skill_name)
        if not body.strip():
            raise SkillValidationError(
                "тело SKILL.md после frontmatter не должно быть пустым",
            )

        parts = [body.strip()]
        for subdir_name in ("references", "routes"):
            subdir = skill_dir / subdir_name
            if not subdir.is_dir():
                continue
            for path in sorted(subdir.rglob("*.md")):
                if path.is_file():
                    rel = path.relative_to(skill_dir).as_posix()
                    file_text = path.read_text(encoding="utf-8").strip()
                    parts.append(f"## {rel}\n\n{file_text}")

        return "\n\n".join(parts)


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

    return raw, parts[2].lstrip("\n")
