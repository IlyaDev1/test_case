import importlib

import pytest
from fastapi.testclient import TestClient

from src.core.abc import FailResult, SuccessResult, UseCaseInterface
from src.presentation.fastapi.app import create_app


@pytest.mark.parametrize(
    "module_path",
    [
        "src.core.abc",
        "src.core.domain.skill",
        "src.core.domain.protocol",
        "src.core.application.skill",
        "src.core.application.protocol",
        "src.infra.skill",
        "src.infra.protocol",
        "src.infra.llm",
        "src.infra.di",
        "src.core.application.llm",
        "src.presentation.fastapi.app",
        "config.bootstrap",
    ],
)
def test_module_imports(module_path: str) -> None:
    importlib.import_module(module_path)


def test_result_types() -> None:
    success = SuccessResult(data={"key": "value"})
    assert success.data == {"key": "value"}

    fail = FailResult(message="error", code="ERR")
    assert fail.message == "error"
    assert fail.code == "ERR"


def test_usecase_interface_is_abstract() -> None:
    with pytest.raises(TypeError):
        UseCaseInterface()  # type: ignore[abstract]


def test_create_app_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_load_runtime_env_does_not_raise() -> None:
    from config.bootstrap import load_runtime_env

    load_runtime_env()
