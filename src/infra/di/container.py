from collections.abc import Iterable

from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from src.infra.di.providers.application import ApplicationProvider
from src.infra.di.providers.infra import InfraProvider


def app_providers() -> tuple[Provider, ...]:
    return (
        InfraProvider(),
        ApplicationProvider(),
    )


def create_container(
    *extra_providers: Provider,
    with_fastapi: bool = False,
) -> AsyncContainer:
    providers: Iterable[Provider] = (
        *app_providers(),
        *extra_providers,
        *((FastapiProvider(),) if with_fastapi else ()),
    )
    return make_async_container(*providers)
