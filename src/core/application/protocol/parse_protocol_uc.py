from src.core.abc.result import FailResult, SuccessResult
from src.core.abc.usecase import UseCaseABC
from src.core.application.protocol.dtos import ParseProtocolDTO, ParseProtocolResult
from src.core.application.protocol.ports import ProtocolTextParserPort
from src.core.domain.protocol.exceptions import ProtocolParseError

PARSE_ERROR_CODE = "PROTOCOL_PARSE_ERROR"


class ParseProtocolUC(UseCaseABC):
    """Разбор markdown-протокола в доменную модель."""

    def __init__(self, *, parser: ProtocolTextParserPort) -> None:
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
