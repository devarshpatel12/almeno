from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from typing import List


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def bulk_create(self, transactions: List[Transaction]):
        self.session.add_all(transactions)
        self.session.commit()

    def list_by_job(self, job_id: str):
        return self.session.query(Transaction).filter_by(job_id=job_id).all()
