from datetime import datetime
import time

from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from .db import Base, engine, SessionLocal
from .models import Job, JobExecution

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


def run_job(job_id: str, execution_id: str):
    """Executa um job e registra resultado na execution (MVP: simulação)."""
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        exe = db.get(JobExecution, execution_id)
        if not job or not exe:
            return

        # RUNNING
        job.status = "RUNNING"
        exe.status = "RUNNING"
        exe.started_at = datetime.utcnow()
        db.commit()

        # Simula trabalho
        time.sleep(2)

        # SUCCESS + output
        exe.status = "SUCCESS"
        exe.output = {"echo": job.payload}
        exe.finished_at = datetime.utcnow()
        job.status = "SUCCESS"
        db.commit()

    except Exception as e:
        job = db.get(Job, job_id)
        exe = db.get(JobExecution, execution_id)
        if job and exe:
            exe.status = "FAILED"
            exe.error_message = str(e)
            exe.finished_at = datetime.utcnow()
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

    exe = JobExecution(job_id=job.id, attempt=1, status="PENDING")
    db.add(exe)
    db.commit()
    db.refresh(exe)

    background.add_task(run_job, str(job.id), str(exe.id))

    return {"job_id": str(job.id), "status": job.status, "execution_id": str(exe.id), "attempt": exe.attempt}

@app.get("/jobs")
def list_jobs(
    status: Optional[str] = None,
    connector_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 200)
    offset = max(offset, 0)

    q = db.query(Job)

    if status:
        q = q.filter(Job.status == status)
    if connector_name:
        q = q.filter(Job.connector_name == connector_name)

    jobs = q.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

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

@app.get("/jobs")
def list_jobs(limit: int = 50, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(min(limit, 200)).all()
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


@app.post("/jobs/{job_id}/retry")
def retry_job(job_id: str, background: BackgroundTasks, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    last_attempt = 0
    for exe in job.executions:
        if exe.attempt > last_attempt:
            last_attempt = exe.attempt

    new_exe = JobExecution(job_id=job.id, attempt=last_attempt + 1, status="PENDING")
    db.add(new_exe)

    job.status = "PENDING"
    db.commit()
    db.refresh(new_exe)

    background.add_task(run_job, str(job.id), str(new_exe.id))

    return {"job_id": str(job.id), "status": job.status, "execution_id": str(new_exe.id), "attempt": new_exe.attempt}
