from typing import Literal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2)
    type: Literal["receita", "despesa"]
    color: str = "#2563eb"
