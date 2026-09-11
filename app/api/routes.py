from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.core.security import require_basic_auth
from app.schemas import CreateUrlRequest

router = APIRouter()


@router.post("/urls")
def create_short_url(
    _payload: CreateUrlRequest,
    _authenticated: Annotated[None, Depends(require_basic_auth)],
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "URL creation is not implemented yet. The HTTP route and Basic "
            "Authentication skeleton are in place."
        ),
    )


@router.get("/{short_code}")
def resolve_short_url(
    short_code: Annotated[str, Path(min_length=1)],
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "message": "Short URL resolution is not implemented yet.",
            "short_code": short_code,
        },
    )
