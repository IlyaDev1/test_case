from src.core.domain.exceptions import DomainError


class LlmError(DomainError):
    """Ошибка вызова LLM-провайдера."""
