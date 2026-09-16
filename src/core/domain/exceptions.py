class DomainError(Exception):
    """Базовая доменная ошибка с сообщением и опциональным контекстом."""

    def __init__(self, message: str, *, context: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context
