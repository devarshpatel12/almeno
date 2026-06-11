from fastapi import APIRouter
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models.job import Job

router = APIRouter()


@router.get("/")
def metrics():
    with SessionLocal() as s:
        total = s.scalar(select(func.count()).select_from(Job)) or 0
        avg = s.scalar(select(func.avg(Job.processing_time_ms))) or 0
        anomalies = s.scalar(select(func.sum(Job.anomalies_detected))) or 0
    return {"jobs_processed": int(total), "avg_processing_time_ms": float(avg or 0), "total_anomalies": int(anomalies or 0)}
