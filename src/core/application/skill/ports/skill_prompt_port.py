from abc import ABC, abstractmethod


class SkillPromptPort(ABC):
    """Порт загрузки системного промпта скилла по имени."""

    @abstractmethod
    def load(self, skill_name: str) -> str:
        """Возвращает текст system prompt для LLM."""
        ...
