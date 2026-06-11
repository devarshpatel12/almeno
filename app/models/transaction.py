from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    txn_id = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    merchant = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    status = Column(String, nullable=True)
    category = Column(String, nullable=True)
    account_id = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(String, nullable=True)
    llm_category = Column(String, nullable=True)
    llm_raw_response = Column(String, nullable=True)
    llm_failed = Column(Boolean, default=False)

    def as_dict(self):
        return {
            "id": self.id,
            "txn_id": self.txn_id,
            "date": self.date.isoformat() if self.date else None,
            "merchant": self.merchant,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "category": self.category,
            "account_id": self.account_id,
            "notes": self.notes,
            "is_anomaly": self.is_anomaly,
            "anomaly_reason": self.anomaly_reason,
            "llm_category": self.llm_category,
            "llm_raw_response": self.llm_raw_response,
            "llm_failed": self.llm_failed,
        }
