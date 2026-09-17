import re

from src.core.abc.result import FailResult, SuccessResult
from src.core.application.llm.exceptions import LlmError
from src.core.application.llm.ports import LlmChatPort
from src.core.application.protocol.constants import (
    LLM_ERROR_CODE,
    PARSE_ERROR_CODE,
    SKILL_NOT_FOUND_CODE,
)
from src.core.application.protocol.usecases.dtos import (
    ExportProtocolDTO,
    ExportProtocolResult,
    GenerateProtocolDTO,
)
from src.core.application.protocol.usecases.export_protocol_uc import (
    ExportProtocolToDocxUC,
)
from src.core.application.skill.exceptions import SkillNotFoundError
from src.core.application.skill.ports import SkillPromptPort

_MAX_LLM_ATTEMPTS = 2
_MARKDOWN_FENCE_RE = re.compile(
    r"^```(?:markdown|md)?\s*\n(.*?)\n```\s*$",
    re.DOTALL | re.IGNORECASE,
)


class GenerateProtocolToDocxUC:
    """Заметки → LLM (skill prompt) → markdown-протокол → Word (.docx)."""

    def __init__(
        self,
        llm: LlmChatPort,
        skill_prompt_loader: SkillPromptPort,
        export_uc: ExportProtocolToDocxUC,
    ) -> None:
        self._llm = llm
        self._skill_prompt_loader = skill_prompt_loader
        self._export_uc = export_uc

    async def execute(
        self,
        dto: GenerateProtocolDTO,
    ) -> SuccessResult | FailResult:
        try:
            system_prompt = self._skill_prompt_loader.load(dto.skill_name)
        except SkillNotFoundError as exc:
            return FailResult(
                message=exc.message,
                code=SKILL_NOT_FOUND_CODE,
                context=exc.context,
            )

        user_message = (
            "Оформи протокол встречи из следующих заметок. "
            "Верни только markdown-протокол по контракту, без пояснений.\n\n"
            f"{dto.notes.strip()}"
        )

        last_parse_error: FailResult | None = None
        for attempt in range(_MAX_LLM_ATTEMPTS):
            try:
                markdown = await self._llm.complete(
                    system_prompt=system_prompt,
                    user_message=user_message,
                )
            except LlmError as exc:
                return FailResult(
                    message=exc.message,
                    code=LLM_ERROR_CODE,
                    context=exc.context,
                )

            export_result = self._export_uc.execute(
                ExportProtocolDTO(text=_normalize_llm_markdown(markdown)),
            )
            if isinstance(export_result, SuccessResult):
                assert isinstance(export_result.data, ExportProtocolResult)
                return export_result

            assert isinstance(export_result, FailResult)
            last_parse_error = export_result
            is_last_attempt = attempt + 1 >= _MAX_LLM_ATTEMPTS
            if export_result.code != PARSE_ERROR_CODE or is_last_attempt:
                return export_result

            user_message = (
                f"{user_message}\n\n"
                "Предыдущий ответ не прошёл валидацию формата. "
                f"Ошибка: {export_result.message}. "
                "Исправь и верни только контрактный markdown-протокол."
            )

        assert last_parse_error is not None
        return last_parse_error


def _normalize_llm_markdown(text: str) -> str:
    cleaned = text.strip()
    fence_match = _MARKDOWN_FENCE_RE.fullmatch(cleaned)
    if fence_match:
        return fence_match.group(1).strip()
    return cleaned
