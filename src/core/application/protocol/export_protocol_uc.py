from src.core.abc.result import FailResult, SuccessResult
from src.core.abc.usecase import UseCaseInterface
from src.core.application.protocol.constants import PARSE_ERROR_CODE
from src.core.application.protocol.dtos import ExportProtocolDTO, ExportProtocolResult
from src.core.application.protocol.services import ProtocolTextParserService
from src.core.domain.protocol.exceptions import ProtocolParseError
from src.infra.protocol.docx_exporter import DocxProtocolExporterService


class ExportProtocolToDocxUC(UseCaseInterface):
    """Разбор markdown-протокола и экспорт в Word (.docx)."""

    def __init__(
        self,
        parser: ProtocolTextParserService,
        exporter: DocxProtocolExporterService,
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

        content = self._exporter.export(protocol)
        return SuccessResult(data=ExportProtocolResult(content=content))
