from src.core.domain.exceptions import DomainError


class ProtocolParseError(DomainError):
    """Текст не соответствует контракту markdown-протокола."""
