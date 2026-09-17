from abc import ABC, abstractmethod


class LlmChatPort(ABC):
    """Порт чат-завершения: system + user → текст ответа модели."""

    @abstractmethod
    async def complete(self, *, system_prompt: str, user_message: str) -> str:
        """Отправляет промпт модели и возвращает текст ответа."""
        raise NotImplementedError
