from src.core.abc.result import FailResult, SuccessResult
from src.core.abc.usecase import UseCaseABC
from src.core.application.protocol.dtos import (
    ExportProtocolDTO,
    ExportProtocolResult,
    ParseProtocolDTO,
    ParseProtocolResult,
)
from src.core.application.protocol.parse_protocol_uc import ParseProtocolUC
from src.infra.protocol.docx_exporter import DocxProtocolExporterService


class ExportProtocolToDocxUC(UseCaseABC):
    """Разбор markdown-протокола и экспорт в Word (.docx)."""

    def __init__(self) -> None:
        self._parse_uc = ParseProtocolUC()
        self._exporter = DocxProtocolExporterService()

    def execute(self, dto: ExportProtocolDTO) -> SuccessResult | FailResult:
        parse_result = self._parse_uc.execute(ParseProtocolDTO(text=dto.text))
        if isinstance(parse_result, FailResult):
            return parse_result

        parse_data = parse_result.data
        assert isinstance(parse_data, ParseProtocolResult)
        content = self._exporter.export(parse_data.protocol)
        return SuccessResult(data=ExportProtocolResult(content=content))
