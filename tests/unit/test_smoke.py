import importlib

import pytest
from fastapi.testclient import TestClient

from src.core.abc import FailResult, SuccessResult, UseCaseABC
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
        "src.presentation.fastapi.app",
        "src.presentation.cli.export_protocol",
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


def test_usecase_abc_is_abstract() -> None:
    with pytest.raises(TypeError):
        UseCaseABC()  # type: ignore[abstract]


def test_create_app_health() -> None:
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
