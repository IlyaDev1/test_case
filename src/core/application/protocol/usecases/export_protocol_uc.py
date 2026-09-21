from src.core.abc.result import FailResult, SuccessResult
from src.core.abc.usecase import UseCaseInterface
from src.core.application.protocol.constants import PARSE_ERROR_CODE
from src.core.application.protocol.ports import ProtocolExporterPort
from src.core.application.protocol.services import ProtocolTextParserService
from src.core.application.protocol.usecases.dtos import (
    ExportProtocolDTO,
    ExportProtocolResult,
)
from src.core.domain.protocol.exceptions import ProtocolParseError


class ExportProtocolToDocxUC(UseCaseInterface):
    """Разбор markdown-протокола и экспорт через ProtocolExporterPort."""

    def __init__(
        self,
        parser: ProtocolTextParserService,
        exporter: ProtocolExporterPort,
    ) -> None:
        self._parser = parser
        self._exporter = exporter

    def execute(self, dto: ExportProtocolDTO) -> SuccessResult | FailResult:
        try:
            protocol = self._parser.parse(dto.text)
        except ProtocolParseError as exc:
            return FailResult(
                message=exc.message,
                code=PARSE_ERROR_CODE,
                context=exc.context,
            )

        artifact = self._exporter.export(protocol)
        return SuccessResult(data=ExportProtocolResult(artifact=artifact))
