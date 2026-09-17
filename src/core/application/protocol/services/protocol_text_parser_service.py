import re

from src.core.domain.protocol.entities import MeetingProtocol, TaskItem
from src.core.domain.protocol.exceptions import ProtocolParseError
from src.core.domain.protocol.placeholders import NO_DATA, NOT_SPECIFIED

TITLE = "# Протокол встречи"
SECTION_METADATA = "## Метаданные"
SECTION_DISCUSSION = "## Обсуждение"
SECTION_DECISIONS = "## Решения"
SECTION_TASKS = "## Задачи"

_SECTION_ORDER = (
    SECTION_METADATA,
    SECTION_DISCUSSION,
    SECTION_DECISIONS,
    SECTION_TASKS,
)

_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_DECISION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
_META_DATE_RE = re.compile(r"^- Дата:\s*(.*)$")
_META_PARTICIPANTS_RE = re.compile(r"^- Участники:\s*(.*)$")
_META_TOPIC_RE = re.compile(r"^- Тема:\s*(.*)$")

_TASKS_HEADER = "| Задача | Ответственный | Срок |"
_TASKS_SEPARATOR_RE = re.compile(r"^\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|$")


class ProtocolTextParserService:
    """Разбор markdown-протокола по жёстким маркерам разделов → MeetingProtocol."""

    def parse(self, text: str) -> MeetingProtocol:
        cleaned = self._strip_html_comments(text).strip()
        if not cleaned:
            raise ProtocolParseError("пустой текст протокола")

        if not cleaned.startswith(TITLE):
            raise ProtocolParseError(
                f"документ должен начинаться с «{TITLE}»",
                context={"preview": cleaned[:80]},
            )

        after_title = cleaned[len(TITLE) :].lstrip("\n")
        sections = self._split_sections(after_title)

        date, participants, topic = self._parse_metadata(sections[SECTION_METADATA])
        discussion = self._parse_discussion(sections[SECTION_DISCUSSION])
        decisions = self._parse_decisions(sections[SECTION_DECISIONS])
        tasks = self._parse_tasks(sections[SECTION_TASKS])

        return MeetingProtocol(
            date=date,
            participants=participants,
            topic=topic,
            discussion=discussion,
            decisions=decisions,
            tasks=tasks,
        )

    @staticmethod
    def _strip_html_comments(text: str) -> str:
        return _HTML_COMMENT_RE.sub("", text)

    def _split_sections(self, body: str) -> dict[str, str]:
        positions: list[tuple[str, int]] = []
        for marker in _SECTION_ORDER:
            idx = body.find(marker)
            if idx < 0:
                raise ProtocolParseError(f"отсутствует раздел «{marker}»")
            positions.append((marker, idx))

        for prev, curr in zip(positions, positions[1:], strict=False):
            if prev[1] >= curr[1]:
                raise ProtocolParseError(
                    "разделы должны идти в порядке: "
                    "Метаданные → Обсуждение → Решения → Задачи",
                    context={"found_order": [m for m, _ in positions]},
                )

        before_first = body[: positions[0][1]].strip()
        if before_first:
            raise ProtocolParseError(
                "лишний текст до раздела «## Метаданные»",
                context={"extra": before_first[:80]},
            )

        result: dict[str, str] = {}
        for i, (marker, start) in enumerate(positions):
            content_start = start + len(marker)
            end = positions[i + 1][1] if i + 1 < len(positions) else len(body)
            result[marker] = body[content_start:end].strip("\n")
        return result

    def _parse_metadata(self, raw: str) -> tuple[str, str, str]:
        lines = [line.rstrip() for line in raw.strip().splitlines() if line.strip()]
        if len(lines) != 3:
            raise ProtocolParseError(
                "метаданные: ожидаются ровно 3 пункта (Дата, Участники, Тема)",
                context={"lines": lines},
            )

        date_m = _META_DATE_RE.fullmatch(lines[0])
        participants_m = _META_PARTICIPANTS_RE.fullmatch(lines[1])
        topic_m = _META_TOPIC_RE.fullmatch(lines[2])
        if not date_m or not participants_m or not topic_m:
            raise ProtocolParseError(
                "метаданные: пункты должны быть "
                "«- Дата:», «- Участники:», «- Тема:» в этом порядке",
                context={"lines": lines},
            )

        return (
            self._scalar(date_m.group(1)),
            self._scalar(participants_m.group(1)),
            self._scalar(topic_m.group(1)),
        )

    def _parse_discussion(self, raw: str) -> str:
        body = raw.strip()
        if not body:
            raise ProtocolParseError(
                "раздел «Обсуждение» пуст: ожидается текст или «нет данных»"
            )
        return body

    def _parse_decisions(self, raw: str) -> tuple[str, ...]:
        body = raw.strip()
        if not body:
            raise ProtocolParseError(
                "раздел «Решения» пуст: ожидается список или «нет данных»"
            )
        if body == NO_DATA:
            return ()

        lines = [line.rstrip() for line in body.splitlines() if line.strip()]
        decisions: list[str] = []
        for expected_n, line in enumerate(lines, start=1):
            match = _DECISION_RE.fullmatch(line)
            if not match:
                raise ProtocolParseError(
                    "решения: ожидается нумерованный список «1. …» "
                    "или одна строка «нет данных»",
                    context={"line": line},
                )
            number = int(match.group(1))
            if number != expected_n:
                raise ProtocolParseError(
                    f"решения: ожидался номер {expected_n}, получен {number}",
                    context={"line": line},
                )
            text = match.group(2).strip()
            if not text:
                raise ProtocolParseError(
                    "решения: пустой пункт списка",
                    context={"line": line},
                )
            decisions.append(text)
        return tuple(decisions)

    def _parse_tasks(self, raw: str) -> tuple[TaskItem, ...]:
        body = raw.strip()
        if not body:
            raise ProtocolParseError(
                "раздел «Задачи» пуст: ожидается таблица или «нет данных»"
            )
        if body == NO_DATA:
            return ()

        lines = [line.rstrip() for line in body.splitlines() if line.strip()]
        if len(lines) < 2:
            raise ProtocolParseError(
                "задачи: нужна markdown-таблица с заголовком и разделителем",
                context={"lines": lines},
            )

        header = self._normalize_table_row(lines[0])
        if header != _TASKS_HEADER:
            raise ProtocolParseError(
                f"задачи: заголовок таблицы должен быть «{_TASKS_HEADER}»",
                context={"header": lines[0]},
            )
        if not _TASKS_SEPARATOR_RE.fullmatch(lines[1].strip()):
            raise ProtocolParseError(
                "задачи: после заголовка нужна строка-разделитель",
                context={"separator": lines[1]},
            )

        tasks: list[TaskItem] = []
        for line in lines[2:]:
            cells = self._split_table_row(line)
            if len(cells) != 3:
                raise ProtocolParseError(
                    "задачи: каждая строка должна иметь ровно 3 колонки",
                    context={"line": line, "cells": cells},
                )
            title = cells[0].strip()
            if not title:
                raise ProtocolParseError(
                    "задачи: пустой текст задачи",
                    context={"line": line},
                )
            tasks.append(
                TaskItem(
                    title=title,
                    assignee=self._scalar(cells[1]),
                    deadline=self._scalar(cells[2]),
                )
            )
        if not tasks:
            raise ProtocolParseError(
                "задачи: таблица без строк — используйте «нет данных»"
            )
        return tuple(tasks)

    @staticmethod
    def _scalar(value: str) -> str:
        cleaned = value.strip()
        return cleaned if cleaned else NOT_SPECIFIED

    @staticmethod
    def _normalize_table_row(line: str) -> str:
        cells = ProtocolTextParserService._split_table_row(line)
        return "| " + " | ".join(cell.strip() for cell in cells) + " |"

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            raise ProtocolParseError(
                "задачи: строка таблицы должна начинаться и заканчиваться «|»",
                context={"line": line},
            )
        inner = stripped[1:-1]
        return inner.split("|")
