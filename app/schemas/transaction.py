from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionOut(BaseModel):
    txn_id: str
    date: Optional[datetime]
    merchant: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    status: Optional[str]
    category: Optional[str]
    account_id: Optional[str]
    notes: Optional[str]
    is_anomaly: Optional[bool]

    class Config:
        orm_mode = True
