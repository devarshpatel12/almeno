import time
import logging
import json
from pathlib import Path
from datetime import datetime
from celery.utils.log import get_task_logger
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal, init_db
from app.repositories.job_repository import JobRepository
from app.services.csv_processor import read_csv, clean_csv_rows, detect_anomalies
from app.services.category_classifier import classify_missing_categories
from app.services.report_generator import generate_reports
from app.services.summary_generator import generate_summary
from app.models.transaction import Transaction
from sqlalchemy.exc import SQLAlchemyError
import uuid

logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_csv_job(self, job_id: str, path: str):
    start = time.time()
    init_db()
    session = SessionLocal()
    repo = JobRepository(session)
    try:
        repo.update_status(job_id, "PROCESSING")
        raw = read_csv(path)
        repo.update_status(job_id, "PROCESSING", row_count_raw=len(raw))
        cleaned = clean_csv_rows(raw)
        repo.update_status(job_id, "PROCESSING", row_count_clean=len(cleaned))
        # anomalies
        anomalies = detect_anomalies(cleaned)
        repo.update_status(job_id, "PROCESSING", anomalies_detected=len(anomalies))
        # classify
        classified = classify_missing_categories(cleaned)
        # persist transactions
        txs = []
        for r in classified:
            tx = Transaction(
                id=str(uuid.uuid4()),
                job_id=job_id,
                txn_id=r.get("txn_id"),
                date=r.get("date"),
                merchant=r.get("merchant"),
                amount=r.get("amount"),
                currency=r.get("currency"),
                status=r.get("status"),
                category=r.get("category") or r.get("llm_category"),
                account_id=r.get("account_id"),
                notes=r.get("notes"),
                is_anomaly=bool(r.get("anomaly_reason")),
                anomaly_reason=",".join(r.get("anomaly_reason") or []) if isinstance(r.get("anomaly_reason"), list) else r.get("anomaly_reason"),
                llm_category=r.get("llm_category"),
                llm_raw_response=r.get("llm_raw_response"),
                llm_failed=r.get("llm_failed", False),
            )
            txs.append(tx)
        session.add_all(txs)
        session.commit()
        summary = generate_summary(classified)
        try:
            uploads_dir = Path(__file__).resolve().parents[2] / "uploads"
            reports = generate_reports(
                job_id,
                summary,
                [t.as_dict() for t in txs],
                uploads_dir,
            )
            logger.info("Report files generated: %s", ", ".join(str(p) for p in reports.values()))
        except Exception:
            logger.exception("Failed to generate report files")

        repo.update_status(
            job_id,
            "COMPLETED",
            summary=summary,
            processing_time_ms=int((time.time() - start) * 1000),
            completed_at=datetime.utcnow(),
        )
    except SQLAlchemyError as exc:
        logger.exception("DB error")
        session.rollback()
        with SessionLocal() as error_session:
            JobRepository(error_session).update_status(job_id, "FAILED", error_message=str(exc))
        raise self.retry(exc=exc)
    except Exception as exc:
        logger.exception("Processing error")
        session.rollback()
        with SessionLocal() as error_session:
            try:
                JobRepository(error_session).update_status(job_id, "FAILED", error_message=str(exc))
            except Exception:
                pass
        raise self.retry(exc=exc)
    finally:
        session.close()
