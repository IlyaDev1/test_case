from dataclasses import dataclass

from src.core.domain.protocol.entities import MeetingProtocol


@dataclass(frozen=True, slots=True)
class ParseProtocolDTO:
    text: str


@dataclass(frozen=True, slots=True)
class ParseProtocolResult:
    protocol: MeetingProtocol
