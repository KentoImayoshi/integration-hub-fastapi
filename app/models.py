import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connector_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PENDING")
    payload = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    executions = relationship(
        "JobExecution",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="JobExecution.attempt.asc()",
    )


class JobExecution(Base):
    __tablename__ = "job_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    attempt = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="PENDING")

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    output = Column(JSONB, nullable=True)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    job = relationship("Job", back_populates="executions")
