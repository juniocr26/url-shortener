from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.controllers.url_controller import (
    create_url,
    resolve_url,
)
from app.core.security import require_basic_auth
from app.schemas import CreateUrlRequest


router = APIRouter()


@router.post(
    "/urls",
    dependencies=[Depends(require_basic_auth)],
)
def create_url_route(
    payload: CreateUrlRequest,
):
    return create_url(payload)


@router.get("/{short_code}")
def resolve_url_route(
    short_code: Annotated[str, Path(min_length=1)],
):
    return resolve_url(short_code)