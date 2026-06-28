from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):
    title: str = Field(min_length=3)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: Optional[date] = None
    status: Literal["ativa", "concluida", "pausada"] = "ativa"
