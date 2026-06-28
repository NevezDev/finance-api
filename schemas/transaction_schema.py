from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    category_id: Optional[int] = None
    description: str = Field(min_length=2)
    type: Literal["receita", "despesa"]
    amount: float = Field(gt=0)
    transaction_date: date
    payment_method: Optional[str] = None
    notes: Optional[str] = None
