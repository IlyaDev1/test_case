from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.core.abc import FailResult, SuccessResult
from src.core.application.llm.exceptions import LlmError
from src.core.application.llm.ports import LlmChatPort
from src.core.application.protocol import (
    ExportProtocolToDocxUC,
    FileArtifact,
    GenerateProtocolDTO,
    GenerateProtocolToDocxUC,
    ProtocolTextParserService,
)
from src.core.application.protocol.constants import (
    LLM_ERROR_CODE,
    PARSE_ERROR_CODE,
    SKILL_NOT_FOUND_CODE,
)
from src.core.application.skill.ports import SkillPromptPort
from src.infra.llm.deepseek_client import DeepSeekClient
from src.infra.protocol.docx_exporter import DocxProtocolExporter
from src.presentation.fastapi.app import create_app

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
NOTES_INPUT = """\
12.03.2026, созвон по релизу 2.1
были: Игорь, Света, Павел

сначала долго про баг с авторизацией — вроде на стороне API, Паша уже смотрит логи
Игорь сказал что дизайн карточки товара ещё плавает,
Света покажет варианты на след. неделе
в итоге решили: релиз не двигаем, остаёмся на 20.03
ещё утвердили что фича «избранное» уходит в 2.2

задачи:
- Павел: пофиксить 401 на /login до 15.03
- Света подготовить 2 макета карточки (срок не сказали)
- кто-то должен обновить changelog — не назначили, к релизу желательно
"""
VALID_PROTOCOL = (EXAMPLES / "notes_to_protocol.md").read_text(encoding="utf-8")
DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


class FakeLlmChatPort(LlmChatPort):
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    async def complete(self, *, system_prompt: str, user_message: str) -> str:
        self.calls.append((system_prompt, user_message))
        if not self._responses:
            raise RuntimeError("no more fake LLM responses")
        return self._responses.pop(0)


class FakeSkillPromptLoader(SkillPromptPort):
    def __init__(self, prompt: str = "system prompt") -> None:
        self._prompt = prompt
        self.requested: list[str] = []

    def load(self, skill_name: str) -> str:
        self.requested.append(skill_name)
        if skill_name == "missing-skill":
            from src.core.application.skill.exceptions import SkillNotFoundError

            raise SkillNotFoundError("скил не найден")
        return self._prompt


@pytest.fixture
def export_uc() -> ExportProtocolToDocxUC:
    return ExportProtocolToDocxUC(
        parser=ProtocolTextParserService(),
        exporter=DocxProtocolExporter(),
    )


@pytest.mark.asyncio
async def test_generate_success(export_uc: ExportProtocolToDocxUC) -> None:
    llm = FakeLlmChatPort([VALID_PROTOCOL])
    loader = FakeSkillPromptLoader("skill body")
    uc = GenerateProtocolToDocxUC(
        llm=llm,
        skill_prompt_loader=loader,
        export_uc=export_uc,
    )

    result = await uc.execute(GenerateProtocolDTO(notes=NOTES_INPUT))

    assert isinstance(result, SuccessResult)
    assert isinstance(result.data.artifact, FileArtifact)
    assert result.data.artifact.body
    assert loader.requested == ["meeting-minutes"]
    assert len(llm.calls) == 1
    assert "skill body" in llm.calls[0][0]
    assert NOTES_INPUT.strip() in llm.calls[0][1]


@pytest.mark.asyncio
async def test_generate_strips_markdown_fence(
    export_uc: ExportProtocolToDocxUC,
) -> None:
    fenced = f"```markdown\n{VALID_PROTOCOL}\n```"
    llm = FakeLlmChatPort([fenced])
    uc = GenerateProtocolToDocxUC(
        llm=llm,
        skill_prompt_loader=FakeSkillPromptLoader(),
        export_uc=export_uc,
    )

    result = await uc.execute(GenerateProtocolDTO(notes=NOTES_INPUT))

    assert isinstance(result, SuccessResult)


@pytest.mark.asyncio
async def test_generate_retries_on_invalid_markdown(
    export_uc: ExportProtocolToDocxUC,
) -> None:
    llm = FakeLlmChatPort(["не протокол", VALID_PROTOCOL])
    uc = GenerateProtocolToDocxUC(
        llm=llm,
        skill_prompt_loader=FakeSkillPromptLoader(),
        export_uc=export_uc,
    )

    result = await uc.execute(GenerateProtocolDTO(notes=NOTES_INPUT))

    assert isinstance(result, SuccessResult)
    assert len(llm.calls) == 2
    assert "Предыдущий ответ не прошёл валидацию" in llm.calls[1][1]


@pytest.mark.asyncio
async def test_generate_fails_after_invalid_llm_output(
    export_uc: ExportProtocolToDocxUC,
) -> None:
    llm = FakeLlmChatPort(["не протокол", "тоже не протокол"])
    uc = GenerateProtocolToDocxUC(
        llm=llm,
        skill_prompt_loader=FakeSkillPromptLoader(),
        export_uc=export_uc,
    )

    result = await uc.execute(GenerateProtocolDTO(notes=NOTES_INPUT))

    assert isinstance(result, FailResult)
    assert result.code == PARSE_ERROR_CODE
    assert len(llm.calls) == 2


@pytest.mark.asyncio
async def test_generate_skill_not_found(export_uc: ExportProtocolToDocxUC) -> None:
    uc = GenerateProtocolToDocxUC(
        llm=FakeLlmChatPort([VALID_PROTOCOL]),
        skill_prompt_loader=FakeSkillPromptLoader(),
        export_uc=export_uc,
    )

    result = await uc.execute(
        GenerateProtocolDTO(notes=NOTES_INPUT, skill_name="missing-skill"),
    )

    assert isinstance(result, FailResult)
    assert result.code == SKILL_NOT_FOUND_CODE


@pytest.mark.asyncio
async def test_generate_llm_error(export_uc: ExportProtocolToDocxUC) -> None:
    llm = FakeLlmChatPort([])
    llm.complete = AsyncMock(side_effect=LlmError("boom"))  # type: ignore[method-assign]
    uc = GenerateProtocolToDocxUC(
        llm=llm,
        skill_prompt_loader=FakeSkillPromptLoader(),
        export_uc=export_uc,
    )

    result = await uc.execute(GenerateProtocolDTO(notes=NOTES_INPUT))

    assert isinstance(result, FailResult)
    assert result.code == LLM_ERROR_CODE


def test_api_generate_protocol_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    async def fake_chat_completions(self, **kwargs: object) -> str:
        return VALID_PROTOCOL

    with patch.object(DeepSeekClient, "chat_completions", fake_chat_completions):
        client = TestClient(create_app())
        response = client.post(
            "/protocol/generate",
            json={"notes": NOTES_INPUT, "skill_name": "meeting-minutes"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(DOCX_MEDIA_TYPE)
    assert len(response.content) > 0
