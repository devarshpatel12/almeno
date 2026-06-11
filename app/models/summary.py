from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from app.core.database import Base


class JobSummary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    total_spend_inr = Column(Integer, default=0)
    total_spend_usd = Column(Integer, default=0)
    top_merchants = Column(JSON, default=[])
    anomaly_count = Column(Integer, default=0)
    risk_level = Column(String, default="LOW")
    narrative = Column(String, nullable=True)
    processing_metrics = Column(JSON, default={})
