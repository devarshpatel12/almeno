from fastapi import APIRouter
from app.core.database import test_connection

router = APIRouter()


@router.get("/")
def health_check():
    db_ok = test_connection()
    return {"api": "healthy", "database": "healthy" if db_ok else "unhealthy"}
