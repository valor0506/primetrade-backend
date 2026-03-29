from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TradeCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    trade_type: Literal["buy", "sell"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("symbol")
    @classmethod
    def symbol_upper(cls, v: str) -> str:
        return v.upper().strip()


class TradeUpdate(BaseModel):
    symbol: Optional[str] = Field(default=None, min_length=1, max_length=20)
    trade_type: Optional[Literal["buy", "sell"]] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    status: Optional[Literal["open", "closed", "cancelled"]] = None
    notes: Optional[str] = Field(default=None, max_length=500)

    @field_validator("symbol")
    @classmethod
    def symbol_upper(cls, v: Optional[str]) -> Optional[str]:
        return v.upper().strip() if v else v


class TradeOut(BaseModel):
    id: int
    owner_id: int
    symbol: str
    trade_type: str
    quantity: float
    price: float
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TradeListOut(BaseModel):
    total: int
    trades: list[TradeOut]