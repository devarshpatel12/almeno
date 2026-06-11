from sqlalchemy.orm import Session
from app.models.summary import JobSummary


class SummaryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, job_id: str, data: dict):
        s = self.session.query(JobSummary).filter_by(job_id=job_id).first()
        if not s:
            s = JobSummary(id=job_id, job_id=job_id, **data)
            self.session.add(s)
        else:
            for k, v in data.items():
                setattr(s, k, v)
        self.session.commit()
        return s
