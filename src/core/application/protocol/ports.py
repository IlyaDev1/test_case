from typing import Protocol

from src.core.domain.protocol.entities import MeetingProtocol


class ProtocolTextParserPort(Protocol):
    """Порт разбора markdown-протокола по жёстким маркерам разделов."""

    def parse(self, text: str) -> MeetingProtocol:
        """Парсит текст. При нарушении контракта — ProtocolParseError."""
        ...
