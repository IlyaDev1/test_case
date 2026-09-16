from typing import Any

import aiohttp

from src.core.application.llm.exceptions import LlmError


class DeepSeekClient:
    """Низкоуровневый HTTP-клиент DeepSeek Chat Completions (OpenAI-compatible)."""

    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        api_key: str,
        base_url: str,
        timeout_sec: float,
    ) -> None:
        self._session = session
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout_sec)

    async def chat_completions(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
    ) -> str:
        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with self._session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self._timeout,
            ) as response:
                body = await response.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise LlmError(
                "ошибка сети при обращении к DeepSeek",
                context={"error": str(exc)},
            ) from exc

        if response.status >= 400:
            raise LlmError(
                "DeepSeek вернул ошибку",
                context={"status": response.status, "body": body},
            )

        try:
            return str(body["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmError(
                "неожиданный формат ответа DeepSeek",
                context={"body": body},
            ) from exc
