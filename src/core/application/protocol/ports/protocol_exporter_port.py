from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core.domain.protocol.entities import MeetingProtocol


@dataclass(frozen=True, slots=True)
class FileArtifact:
    body: bytes
    media_type: str
    filename: str


@dataclass(frozen=True, slots=True)
class LinkArtifact:
    url: str


type ProtocolArtifact = FileArtifact | LinkArtifact


class ProtocolExporterPort(ABC):
    """Порт: MeetingProtocol → файл или ссылка."""

    @abstractmethod
    def export(self, protocol: MeetingProtocol) -> ProtocolArtifact: ...
