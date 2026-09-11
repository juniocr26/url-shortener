from pydantic import BaseModel, Field


class CreateUrlRequest(BaseModel):
    url: str = Field(
        ...,
        min_length=1,
        description="Initial URL input placeholder; the definitive contract is still planned.",
    )
