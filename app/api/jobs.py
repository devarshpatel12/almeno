import uuid
import shutil
import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import select
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction
from app.repositories.job_repository import JobRepository
from app.services.report_generator import ensure_report_format
from app.workers.tasks import process_csv_job

router = APIRouter()
base_dir = Path(__file__).resolve().parents[2]
uploads_dir = base_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_csv(file: UploadFile = File(...)):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    contents = file.file.read()
    max_size = settings.UPLOAD_MAX_SIZE
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="File too large")
    filename = f"{int(time.time())}_{file.filename}"
    path = uploads_dir / filename
    with open(path, "wb") as f:
        f.write(contents)
    repo = JobRepository(SessionLocal())
    job = repo.create(filename=str(path.name))
    # queue background task
    process_csv_job.apply_async(args=[job.id, str(path)], queue="transactions")
    return {"job_id": job.id, "status": job.status}


@router.get("/")
def list_jobs(status: str | None = Query(None)):
    with SessionLocal() as s:
        q = select(Job)
        if status:
            q = q.where(Job.status == status.upper())
        res = s.execute(q).scalars().all()
        return [r.as_dict() for r in res]


@router.get("/{job_id}/status")
def job_status(job_id: str):
    with SessionLocal() as s:
        job = s.get(Job, job_id)
        if not job:
            raise HTTPException(404, "job not found")
        out = {"job_id": job.id, "status": job.status}
        if job.status == "COMPLETED":
            out["summary"] = job.summary or {}
        return out


@router.get("/{job_id}/results")
def job_results(job_id: str):
    with SessionLocal() as s:
        job = s.get(Job, job_id)
        if not job:
            raise HTTPException(404, "job not found")
        transactions = s.execute(select(Transaction).where(Transaction.job_id == job_id)).scalars().all()
        return {
            "job_id": job.id,
            "status": job.status,
            "transactions": [t.as_dict() for t in transactions],
            "summary": job.summary or {},
        }


@router.get("/{job_id}/download-report")
def download_report(job_id: str, format: str | None = Query(None, pattern="^(json|csv|pdf|zip)$")):
    with SessionLocal() as s:
        job = s.get(Job, job_id)
        if not job:
            raise HTTPException(404, "job not found")
        fmt = format or "json"
        report_path = uploads_dir / f"report_{job.id}.{fmt}"
        if not report_path.exists():
            transactions = s.execute(select(Transaction).where(Transaction.job_id == job_id)).scalars().all()
            try:
                report_path = ensure_report_format(
                    job.id,
                    job.summary or {},
                    [t.as_dict() for t in transactions],
                    uploads_dir,
                    fmt,
                )
            except Exception:
                raise HTTPException(500, "Failed to generate report")
            if not report_path.exists():
                raise HTTPException(500, detail=f"Report generation failed: {report_path}")
        if fmt == "json":
            return FileResponse(str(report_path), media_type="application/json", filename=report_path.name)
        if fmt == "csv":
            return FileResponse(str(report_path), media_type="text/csv", filename=report_path.name)
        if fmt == "pdf":
            return FileResponse(str(report_path), media_type="application/pdf", filename=report_path.name)
        if fmt == "zip":
            return FileResponse(str(report_path), media_type="application/zip", filename=report_path.name)
        raise HTTPException(400, "Unsupported format")
