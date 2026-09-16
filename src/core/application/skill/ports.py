from abc import ABC, abstractmethod

from src.core.domain.skill.entities import SkillMeta


class SkillSourceInterface(ABC):
    """Порт загрузки метаданных скилов из внешнего источника (ФС, БД, API)."""

    @abstractmethod
    def load_all(self) -> tuple[SkillMeta, ...]: ...
