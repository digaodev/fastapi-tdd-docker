from datetime import datetime

from sqlmodel import Field, SQLModel


class TextSummary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
