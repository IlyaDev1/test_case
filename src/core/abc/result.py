from dataclasses import dataclass
from typing import Any


@dataclass
class SuccessResult:
    """Успешный результат выполнения use case."""

    data: Any | None = None


@dataclass
class FailResult:
    """Ошибка выполнения use case."""

    message: str
    code: str
    context: Any = None
