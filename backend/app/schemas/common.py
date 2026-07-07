from pydantic import BaseModel, Field


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
