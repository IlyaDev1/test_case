class ProtocolParseError(Exception):
    """Текст не соответствует контракту markdown-протокола."""

    def __init__(self, message: str, *, context: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context
