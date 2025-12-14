from pydantic import BaseModel, HttpUrl


class SummaryPayloadSchema(BaseModel):
    url: HttpUrl  # validates it's actually a URL


class SummaryResponseSchema(BaseModel):
    id: int
    url: str

    model_config = {"from_attributes": True}  # Enable ORM mode for SQLModel
