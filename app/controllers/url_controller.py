from fastapi.responses import RedirectResponse

from app.schemas import CreateUrlRequest
from app.services.url_service import (
    create_short_url,
    resolve_short_url,
)


def create_url(payload: CreateUrlRequest) -> dict[str, str]:
    return create_short_url(payload)


def resolve_url(short_code: str) -> RedirectResponse:
    destination_url = resolve_short_url(short_code)

    return RedirectResponse(
        url=destination_url,
        status_code=301,
    )