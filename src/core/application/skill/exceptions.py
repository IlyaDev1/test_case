from src.core.domain.exceptions import DomainError


class SkillNotFoundError(DomainError):
    """Скил с указанным именем не найден."""
