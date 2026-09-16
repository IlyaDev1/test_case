from src.core.domain.exceptions import DomainError


class SkillValidationError(DomainError):
    """SKILL.md не проходит правила доменной валидации."""
