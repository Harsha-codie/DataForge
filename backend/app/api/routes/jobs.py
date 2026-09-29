from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.user import User
from app.models.job import BackgroundJob
from app.schemas.job import JobStatusResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])

@router.get("/", response_model=List[JobStatusResponse])
def list_jobs(
    dataset_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(BackgroundJob).filter(BackgroundJob.user_id == current_user.id)
    if dataset_id:
        q = q.filter(BackgroundJob.dataset_id == dataset_id)
    jobs = q.order_by(desc(BackgroundJob.created_at)).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(BackgroundJob).filter(
        BackgroundJob.id == job_id,
        BackgroundJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Background job not found.")
    return job

@router.post("/{job_id}/cancel", response_model=JobStatusResponse)
def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(BackgroundJob).filter(
        BackgroundJob.id == job_id,
        BackgroundJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Background job not found.")

    if job.status in ("completed", "failed"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel job with status '{job.status}'.")

    job.status = "cancelled"
    job.message = "Job cancelled by user."
    job.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
