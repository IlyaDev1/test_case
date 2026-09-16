from config.settings import DeepSeekSettings
from src.core.application.llm.exceptions import LlmError
from src.core.application.llm.ports import LlmChatPort
from src.infra.llm.deepseek_client import DeepSeekClient


class DeepSeekGateway(LlmChatPort):
    """Адаптер DeepSeek Chat Completions к порту LlmChatPort."""

    def __init__(
        self,
        client: DeepSeekClient,
        settings: DeepSeekSettings,
    ) -> None:
        self._client = client
        self._settings = settings

    async def complete(self, *, system_prompt: str, user_message: str) -> str:
        if not system_prompt.strip():
            raise LlmError("system prompt пуст")
        if not user_message.strip():
            raise LlmError("user message пуст")

        return await self._client.chat_completions(
            model=self._settings.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
        )
