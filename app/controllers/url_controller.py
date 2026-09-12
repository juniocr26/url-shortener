from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from app.schemas import CreateUrlRequest, CreateUrlResponse
from app.services.url_service import (
    InvalidShortCode,
    ShortCodeNotFound,
    UrlShortenerConfigurationError,
    UrlShortenerInfrastructureError,
    UrlShortenerService,
)


def create_url(
    payload: CreateUrlRequest,
    service: UrlShortenerService,
) -> CreateUrlResponse:
    try:
        return service.create_short_url(payload)
    except UrlShortenerConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="URL shortener configuration is incomplete.",
        ) from exc
    except UrlShortenerInfrastructureError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL shortener infrastructure is unavailable.",
        ) from exc


def resolve_url(
    short_code: str,
    service: UrlShortenerService,
) -> RedirectResponse:
    try:
        destination_url = service.resolve_short_url(short_code)
    except (InvalidShortCode, ShortCodeNotFound) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short code not found.",
        ) from exc
    except UrlShortenerConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="URL shortener configuration is incomplete.",
        ) from exc
    except UrlShortenerInfrastructureError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL shortener infrastructure is unavailable.",
        ) from exc

    return RedirectResponse(
        url=destination_url,
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )
