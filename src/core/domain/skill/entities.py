import re
from dataclasses import dataclass

from src.core.domain.skill.exceptions import SkillValidationError

_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_MAX_NAME_LEN = 64
_MAX_DESCRIPTION_LEN = 1024


@dataclass(frozen=True, slots=True)
class SkillMeta:
    """Метаданные скилла из SKILL.md (без тела инструкций)."""

    name: str
    caption: str
    description: str
    has_files: bool

    @classmethod
    def create(
        cls,
        *,
        name: str,
        caption: str,
        description: str,
        body: str,
        has_files: bool,
    ) -> "SkillMeta":
        """Создаёт SkillMeta после проверки полей и тела SKILL.md.

        body используется только для валидации и не сохраняется.
        """
        cls._validate_name(name)
        cls._validate_description(description)
        cls._validate_body(body)
        return cls(
            name=name,
            caption=caption,
            description=description.strip(),
            has_files=has_files,
        )

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name:
            raise SkillValidationError("name обязателен", context={"name": name})
        if len(name) > _MAX_NAME_LEN:
            raise SkillValidationError(
                f"name не длиннее {_MAX_NAME_LEN} символов",
                context={"name": name, "length": len(name)},
            )
        if not _NAME_RE.match(name):
            raise SkillValidationError(
                "name должен быть в kebab-case (a-z, 0-9, дефисы)",
                context={"name": name},
            )

    @staticmethod
    def _validate_description(description: str) -> None:
        if not description or not str(description).strip():
            raise SkillValidationError("description обязателен")
        if len(description) > _MAX_DESCRIPTION_LEN:
            raise SkillValidationError(
                f"description не длиннее {_MAX_DESCRIPTION_LEN} символов",
                context={"length": len(description)},
            )

    @staticmethod
    def _validate_body(body: str) -> None:
        if not body or not body.strip():
            raise SkillValidationError(
                "тело SKILL.md после frontmatter не должно быть пустым",
            )
