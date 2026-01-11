from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl

# Status types for type safety
SummaryStatus = Literal["pending", "processing", "completed", "failed"]


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
    status: SummaryStatus
    created_at: datetime

    model_config = {"from_attributes": True}  # Enable ORM mode for SQLModel
