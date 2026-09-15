from abc import ABC, abstractmethod
from typing import Any

from src.core.abc.result import FailResult, SuccessResult


class UseCaseABC(ABC):
    """Базовый класс сценария использования."""

    @abstractmethod
    def execute(self, dto: Any) -> SuccessResult | FailResult:
        raise NotImplementedError
