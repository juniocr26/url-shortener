from app.schemas import CreateUrlRequest


def create_short_url(payload: CreateUrlRequest) -> dict[str, str]:
    return {
        "message": "Reached POST /urls route.",
    }


def resolve_short_url(short_code: str) -> str:
    raise NotImplementedError(
        "Short URL resolution is not implemented yet."
    )