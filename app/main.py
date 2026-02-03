from datetime import datetime
import time

from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from .models import Job

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpaceX Integration Hub (MVP)")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class JobCreate(BaseModel):
    connector_name: str
    payload: dict

def run_job(job_id: str):
    """Simula execução do job (MVP). Depois trocamos por Redis/Celery."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return

        job.status = "RUNNING"
        db.commit()

        # Simula trabalho (ex.: chamar API externa)
        time.sleep(2)

        job.status = "SUCCESS"
        db.commit()
    except Exception:
        # Em MVP, se der erro marca FAILED (sem detalhes ainda)
        job = db.get(Job, job_id)
        if job:
            job.status = "FAILED"
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}

@app.post("/jobs")
def create_job(body: JobCreate, background: BackgroundTasks, db: Session = Depends(get_db)):
    job = Job(connector_name=body.connector_name, payload=body.payload, status="PENDING")
    db.add(job)
    db.commit()
    db.refresh(job)

    # dispara em background
    background.add_task(run_job, str(job.id))

    return {"job_id": str(job.id), "status": job.status}

@app.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": str(job.id),
        "connector_name": job.connector_name,
        "status": job.status,
        "payload": job.payload,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }

@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return [
        {
            "job_id": str(j.id),
            "connector_name": j.connector_name,
            "status": j.status,
            "created_at": j.created_at,
            "updated_at": j.updated_at,
        }
        for j in jobs
    ]
