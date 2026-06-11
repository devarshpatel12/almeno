from fastapi import FastAPI
from app.api import jobs, health, metrics
from app.core.logging import setup_logging
from app.core.database import init_db

setup_logging()

app = FastAPI(title="AI-Powered Transaction Processing Pipeline")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(health.router, prefix="/health")
app.include_router(metrics.router, prefix="/metrics")
app.include_router(jobs.router, prefix="/jobs")

@app.get("/")
async def root():
    return {"service": "ai-transaction-pipeline", "status": "ok"}
