from pydantic import BaseModel
from typing import Dict, List


class SummaryOut(BaseModel):
    total_spend_by_currency: Dict[str, float]
    top_3_merchants: List[str]
    anomaly_count: int
    narrative: str
    risk_level: str
