from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.dependencies import get_url_shortener_service
from app.controllers.url_controller import (
    create_url,
    resolve_url,
)
from app.core.security import require_basic_auth
from app.schemas import CreateUrlRequest, CreateUrlResponse
from app.services.url_service import UrlShortenerService


router = APIRouter()


@router.post(
    "/urls",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateUrlResponse,
    summary="Create a shortened URL",
    dependencies=[Depends(require_basic_auth)],
)
def create_url_route(
    payload: CreateUrlRequest,
    service: Annotated[
        UrlShortenerService,
        Depends(get_url_shortener_service),
    ],
):
    return create_url(payload, service)


@router.get(
    "/{short_code}",
    summary="Resolve a public short code",
    responses={
        status.HTTP_301_MOVED_PERMANENTLY: {
            "description": "Permanent redirect to the original URL.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Short code was not found.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Backing infrastructure is unavailable.",
        },
    },
)
def resolve_url_route(
    short_code: Annotated[str, Path(min_length=1)],
    service: Annotated[
        UrlShortenerService,
        Depends(get_url_shortener_service),
    ],
):
    return resolve_url(short_code, service)
