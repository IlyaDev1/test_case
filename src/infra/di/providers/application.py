from dishka import Provider, Scope, provide

from src.core.application.llm.ports import LlmChatPort
from src.core.application.protocol.services import ProtocolTextParserService
from src.core.application.protocol.usecases import (
    ExportProtocolToDocxUC,
    GenerateProtocolToDocxUC,
    ParseProtocolUC,
)
from src.core.application.skill.ports import SkillPromptPort


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    parser = provide(ProtocolTextParserService)
    parse_protocol_uc = provide(ParseProtocolUC)
    export_protocol_to_docx_uc = provide(ExportProtocolToDocxUC)

    @provide
    def generate_protocol_to_docx_uc(
        self,
        llm: LlmChatPort,
        skill_prompt_loader: SkillPromptPort,
        export_protocol_to_docx_uc: ExportProtocolToDocxUC,
    ) -> GenerateProtocolToDocxUC:
        return GenerateProtocolToDocxUC(
            llm=llm,
            skill_prompt_loader=skill_prompt_loader,
            export_uc=export_protocol_to_docx_uc,
        )
