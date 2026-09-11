import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import get_settings

security = HTTPBasic()


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


def require_basic_auth(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> None:
    settings = get_settings()

    if not settings.basic_auth_configured:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Basic authentication is not configured.",
        )

    expected_username = settings.basic_auth_username or ""
    expected_password = settings.basic_auth_password or ""

    username_matches = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        expected_username.encode("utf-8"),
    )
    password_matches = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        expected_password.encode("utf-8"),
    )

    if not (username_matches and password_matches):
        raise _unauthorized()
