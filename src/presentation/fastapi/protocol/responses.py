from fastapi.responses import RedirectResponse, Response

from src.core.application.protocol.ports import ProtocolArtifact


def artifact_to_response(artifact: ProtocolArtifact) -> Response:
    """HTTP: файл → download, ссылка → redirect."""
    if artifact.kind == "link":
        if not artifact.url:
            raise ValueError("link-артефакт без url")
        return RedirectResponse(url=artifact.url, status_code=302)

    if not artifact.body:
        raise ValueError("file-артефакт без body")

    headers = {}
    if artifact.filename:
        headers["Content-Disposition"] = f'attachment; filename="{artifact.filename}"'
    return Response(
        content=artifact.body,
        media_type=artifact.media_type or "application/octet-stream",
        headers=headers,
    )
