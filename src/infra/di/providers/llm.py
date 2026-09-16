from collections.abc import AsyncIterator

import aiohttp
from dishka import Provider, Scope, provide

from config.settings import DeepSeekSettings
from src.core.application.llm.ports import LlmChatPort
from src.infra.llm.deepseek_client import DeepSeekClient
from src.infra.llm.deepseek_gateway import DeepSeekGateway


class LlmProvider(Provider):
    scope = Scope.APP

    @provide
    def deepseek_settings(self) -> DeepSeekSettings:
        return DeepSeekSettings.from_env()

    @provide
    async def aiohttp_session(self) -> AsyncIterator[aiohttp.ClientSession]:
        session = aiohttp.ClientSession()
        yield session
        await session.close()

    @provide
    def deepseek_client(
        self,
        session: aiohttp.ClientSession,
        settings: DeepSeekSettings,
    ) -> DeepSeekClient:
        return DeepSeekClient(
            session=session,
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout_sec=settings.timeout_sec,
        )

    @provide
    def llm_chat_port(
        self,
        client: DeepSeekClient,
        settings: DeepSeekSettings,
    ) -> LlmChatPort:
        return DeepSeekGateway(client=client, settings=settings)
