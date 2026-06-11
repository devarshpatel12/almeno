import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    row_count_raw = Column(Integer, default=0)
    row_count_clean = Column(Integer, default=0)
    duplicates_removed = Column(Integer, default=0)
    anomalies_detected = Column(Integer, default=0)
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)
    summary = Column(JSON, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status,
            "row_count_raw": self.row_count_raw,
            "row_count_clean": self.row_count_clean,
            "anomalies_detected": self.anomalies_detected,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
