from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SummaryPayloadSchema(BaseModel):
    url: HttpUrl  # validates it's actually a URL


class SummaryUpdateSchema(BaseModel):
    """Schema for updating a summary."""

    url: HttpUrl
    summary: str


class SummaryResponseSchema(BaseModel):
    id: int
    url: str
    summary: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Enable ORM mode for SQLModel
