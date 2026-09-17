from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from src.core.abc.result import FailResult, SuccessResult
from src.core.application.protocol import (
    LLM_ERROR_CODE,
    SKILL_NOT_FOUND_CODE,
    ExportProtocolDTO,
    ExportProtocolResult,
    ExportProtocolToDocxUC,
    GenerateProtocolDTO,
    GenerateProtocolToDocxUC,
)
from src.presentation.fastapi.protocol.schemas import (
    ExportProtocolRequest,
    GenerateProtocolRequest,
)

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
DOCX_FILENAME = "protocol.docx"

protocol_router = APIRouter(
    prefix="/protocol",
    tags=["protocol"],
    route_class=DishkaRoute,
)


def _docx_response(content: bytes) -> Response:
    return Response(
        content=content,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{DOCX_FILENAME}"'},
    )


@protocol_router.post("/export")
def export_protocol(
    body: ExportProtocolRequest,
    uc: FromDishka[ExportProtocolToDocxUC],
) -> Response:
    result = uc.execute(ExportProtocolDTO(text=body.text))

    if isinstance(result, FailResult):
        raise HTTPException(status_code=422, detail=result.message)

    assert isinstance(result, SuccessResult)
    assert isinstance(result.data, ExportProtocolResult)
    return _docx_response(result.data.content)


@protocol_router.post("/generate")
async def generate_protocol(
    body: GenerateProtocolRequest,
    uc: FromDishka[GenerateProtocolToDocxUC],
) -> Response:
    result = await uc.execute(
        GenerateProtocolDTO(notes=body.notes, skill_name=body.skill_name),
    )

    if isinstance(result, FailResult):
        if result.code == SKILL_NOT_FOUND_CODE:
            raise HTTPException(status_code=404, detail=result.message)
        if result.code == LLM_ERROR_CODE:
            raise HTTPException(status_code=502, detail=result.message)
        raise HTTPException(status_code=422, detail=result.message)

    assert isinstance(result, SuccessResult)
    assert isinstance(result.data, ExportProtocolResult)
    return _docx_response(result.data.content)
