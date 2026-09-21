from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, Self

from src.core.domain.protocol.entities import MeetingProtocol


@dataclass(frozen=True, slots=True)
class ProtocolArtifact:
    """Нейтральный результат рендера протокола: файл или ссылка."""

    kind: Literal["file", "link"]
    media_type: str | None = None
    body: bytes | None = None
    filename: str | None = None
    url: str | None = None

    @classmethod
    def file(
        cls,
        *,
        body: bytes,
        media_type: str,
        filename: str,
    ) -> Self:
        return cls(kind="file", body=body, media_type=media_type, filename=filename)

    @classmethod
    def link(cls, *, url: str) -> Self:
        return cls(kind="link", url=url)


class ProtocolExporterPort(ABC):
    """Порт: MeetingProtocol → артефакт (файл / ссылка)."""

    @abstractmethod
    def export(self, protocol: MeetingProtocol) -> ProtocolArtifact: ...
