from dishka import Provider, Scope, provide

from src.core.application.protocol.export_protocol_uc import ExportProtocolToDocxUC
from src.core.application.protocol.parse_protocol_uc import ParseProtocolUC
from src.core.application.protocol.services import ProtocolTextParserService


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    parser = provide(ProtocolTextParserService)
    parse_protocol_uc = provide(ParseProtocolUC)
    export_protocol_to_docx_uc = provide(ExportProtocolToDocxUC)
