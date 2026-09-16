from pathlib import Path

import pytest

from src.core.abc import FailResult, SuccessResult
from src.core.application.protocol import (
    PARSE_ERROR_CODE,
    ParseProtocolDTO,
    ParseProtocolResult,
    ParseProtocolUC,
    ProtocolTextParserService,
)
from src.core.domain.protocol import (
    NO_DATA,
    NOT_SPECIFIED,
    MeetingProtocol,
    ProtocolParseError,
    TaskItem,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def parser_service() -> ProtocolTextParserService:
    return ProtocolTextParserService()


@pytest.fixture
def uc(parser_service: ProtocolTextParserService) -> ParseProtocolUC:
    return ParseProtocolUC(parser=parser_service)


def test_parse_full_example(parser_service: ProtocolTextParserService) -> None:
    text = (EXAMPLES / "notes_to_protocol.md").read_text(encoding="utf-8")
    protocol = parser_service.parse(text)

    assert protocol.date == "12.03.2026"
    assert protocol.participants == "Игорь, Света, Павел"
    assert protocol.topic == "Релиз 2.1"
    assert "баг авторизации" in protocol.discussion
    assert protocol.decisions == (
        "Дату релиза 2.1 не переносить, целевая дата — 20.03.",
        "Фичу «избранное» перенести в релиз 2.2.",
    )
    assert protocol.tasks == (
        TaskItem(
            title="Исправить ошибку 401 на /login",
            assignee="Павел",
            deadline="15.03",
        ),
        TaskItem(
            title="Подготовить 2 макета карточки товара",
            assignee="Света",
            deadline=NOT_SPECIFIED,
        ),
        TaskItem(
            title="Обновить changelog к релизу",
            assignee=NOT_SPECIFIED,
            deadline="20.03",
        ),
    )


def test_parse_missing_assignee_and_deadline(
    parser_service: ProtocolTextParserService,
) -> None:
    text = (FIXTURES / "protocol_missing_assignee_deadline.md").read_text(
        encoding="utf-8"
    )
    protocol = parser_service.parse(text)

    assert protocol.tasks[0].assignee == NOT_SPECIFIED
    assert protocol.tasks[0].deadline == NOT_SPECIFIED
    assert protocol.tasks[1].deadline == NOT_SPECIFIED
    assert protocol.tasks[2].assignee == NOT_SPECIFIED


def test_parse_empty_sections(parser_service: ProtocolTextParserService) -> None:
    text = (FIXTURES / "protocol_empty_sections.md").read_text(encoding="utf-8")
    protocol = parser_service.parse(text)

    assert protocol.date == NOT_SPECIFIED
    assert protocol.participants == NOT_SPECIFIED
    assert protocol.topic == NOT_SPECIFIED
    assert protocol.discussion == NO_DATA
    assert protocol.decisions == ()
    assert protocol.tasks == ()


def test_parse_broken_format_raises(
    parser_service: ProtocolTextParserService,
) -> None:
    with pytest.raises(ProtocolParseError, match="начинаться"):
        parser_service.parse("просто текст без протокола")


@pytest.mark.parametrize(
    "broken",
    [
        "# Протокол встречи\n\n## Обсуждение\nтекст\n",
        (
            "# Протокол встречи\n\n"
            "## Метаданные\n"
            "- Дата: 1\n"
            "- Участники: 2\n"
            "- Тема: 3\n\n"
            "## Решения\nнет данных\n\n"
            "## Обсуждение\nx\n\n"
            "## Задачи\nнет данных\n"
        ),
        (
            "# Протокол встречи\n\n"
            "## Метаданные\n"
            "- Дата: 1\n"
            "- Тема: без участников\n"
            "- Участники: x\n\n"
            "## Обсуждение\nx\n\n"
            "## Решения\nнет данных\n\n"
            "## Задачи\nнет данных\n"
        ),
        (
            "# Протокол встречи\n\n"
            "## Метаданные\n"
            "- Дата: 1\n"
            "- Участники: 2\n"
            "- Тема: 3\n\n"
            "## Обсуждение\nx\n\n"
            "## Решения\n"
            "2. не с единицы\n\n"
            "## Задачи\nнет данных\n"
        ),
        (
            "# Протокол встречи\n\n"
            "## Метаданные\n"
            "- Дата: 1\n"
            "- Участники: 2\n"
            "- Тема: 3\n\n"
            "## Обсуждение\nx\n\n"
            "## Решения\nнет данных\n\n"
            "## Задачи\n"
            "| A | B |\n"
            "|---|---|\n"
            "| x | y |\n"
        ),
    ],
)
def test_parse_various_broken_formats(
    parser_service: ProtocolTextParserService, broken: str
) -> None:
    with pytest.raises(ProtocolParseError):
        parser_service.parse(broken)


def test_parse_protocol_uc_success(uc: ParseProtocolUC) -> None:
    text = (EXAMPLES / "notes_to_protocol.md").read_text(encoding="utf-8")
    result = uc.execute(ParseProtocolDTO(text=text))

    assert isinstance(result, SuccessResult)
    assert isinstance(result.data, ParseProtocolResult)
    assert isinstance(result.data.protocol, MeetingProtocol)
    assert result.data.protocol.topic == "Релиз 2.1"


def test_parse_protocol_uc_fail_on_broken(uc: ParseProtocolUC) -> None:
    result = uc.execute(ParseProtocolDTO(text="не протокол"))

    assert isinstance(result, FailResult)
    assert result.code == PARSE_ERROR_CODE
    assert "Протокол встречи" in result.message
