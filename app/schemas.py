from pydantic import BaseModel, Field, HttpUrl


class CreateUrlRequest(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="HTTP or HTTPS URL that should be shortened.",
    )


class CreateUrlResponse(BaseModel):
    short_code: str = Field(
        ...,
        min_length=7,
        max_length=7,
        description="Seven-character public short code.",
    )
    short_url: str = Field(
        ...,
        description="Complete public short URL.",
    )
