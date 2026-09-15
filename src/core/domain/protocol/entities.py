from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaskItem:
    """Строка таблицы задач протокола."""

    title: str
    assignee: str
    deadline: str


@dataclass(frozen=True, slots=True)
class MeetingProtocol:
    """Структурированный протокол встречи."""

    date: str
    participants: str
    topic: str
    discussion: str
    decisions: tuple[str, ...]
    tasks: tuple[TaskItem, ...]
