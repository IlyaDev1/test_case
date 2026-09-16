from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from src.core.abc.result import FailResult, SuccessResult
from src.core.application.protocol import ExportProtocolDTO, ExportProtocolResult
from src.core.application.protocol.export_protocol_uc import ExportProtocolToDocxUC

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
DOCX_FILENAME = "protocol.docx"

protocol_router = APIRouter(
    prefix="/protocol",
    tags=["protocol"],
    route_class=DishkaRoute,
)


class ExportProtocolRequest(BaseModel):
    text: str


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
    return Response(
        content=result.data.content,
        media_type=DOCX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{DOCX_FILENAME}"'},
    )
