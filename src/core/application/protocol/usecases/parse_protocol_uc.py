from src.core.abc.result import FailResult, SuccessResult
from src.core.abc.usecase import UseCaseInterface
from src.core.application.protocol.constants import PARSE_ERROR_CODE
from src.core.application.protocol.services import ProtocolTextParserService
from src.core.application.protocol.usecases.dtos import (
    ParseProtocolDTO,
    ParseProtocolResult,
)
from src.core.domain.protocol.exceptions import ProtocolParseError


class ParseProtocolUC(UseCaseInterface):
    """Разбор markdown-протокола в доменную модель."""

    def __init__(self, parser: ProtocolTextParserService) -> None:
        self._parser = parser

    def execute(self, dto: ParseProtocolDTO) -> SuccessResult | FailResult:
        try:
            protocol = self._parser.parse(dto.text)
        except ProtocolParseError as exc:
            return FailResult(
                message=exc.message,
                code=PARSE_ERROR_CODE,
                context=exc.context,
            )
        return SuccessResult(data=ParseProtocolResult(protocol=protocol))
