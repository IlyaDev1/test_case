from fastapi.responses import RedirectResponse, Response

from src.core.application.protocol.ports import (
    FileArtifact,
    LinkArtifact,
    ProtocolArtifact,
)


def artifact_to_response(artifact: ProtocolArtifact) -> Response:
    """HTTP: файл → download, ссылка → redirect."""
    match artifact:
        case LinkArtifact(url=url):
            return RedirectResponse(url=url, status_code=302)
        case FileArtifact(body=body, media_type=media_type, filename=filename):
            return Response(
                content=body,
                media_type=media_type,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
