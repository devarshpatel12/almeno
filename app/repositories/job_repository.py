from sqlalchemy.orm import Session
from app.models.job import Job
from datetime import datetime


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, filename: str) -> Job:
        job = Job(filename=filename, status="PENDING", created_at=datetime.utcnow())
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def update_status(self, job_id: str, status: str, **kwargs):
        job = self.session.get(Job, job_id)
        if not job:
            return None
        job.status = status
        for k, v in kwargs.items():
            setattr(job, k, v)
        self.session.commit()
        return job
