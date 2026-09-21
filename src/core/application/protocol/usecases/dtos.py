from dataclasses import dataclass

from src.core.application.protocol.ports import ProtocolArtifact
from src.core.domain.protocol.entities import MeetingProtocol


@dataclass(frozen=True, slots=True)
class ParseProtocolDTO:
    text: str


@dataclass(frozen=True, slots=True)
class ParseProtocolResult:
    protocol: MeetingProtocol


@dataclass(frozen=True, slots=True)
class ExportProtocolDTO:
    text: str


@dataclass(frozen=True, slots=True)
class ExportProtocolResult:
    artifact: ProtocolArtifact


@dataclass(frozen=True, slots=True)
class GenerateProtocolDTO:
    notes: str
    skill_name: str = "meeting-minutes"
