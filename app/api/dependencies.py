from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.services.url_service import UrlShortenerService


def get_url_shortener_service(request: Request) -> UrlShortenerService:
    try:
        id_generator = request.app.state.id_generator
        url_store = request.app.state.url_store
    except AttributeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application dependencies are not initialized.",
        ) from exc

    return UrlShortenerService(
        id_generator=id_generator,
        url_store=url_store,
        settings=get_settings(),
    )
