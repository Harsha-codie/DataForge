import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import polars as pl
from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.version import DatasetVersion
from app.models.ml_readiness import MLReadinessReport
from app.schemas.ml_readiness import MLReadinessRequest, MLReadinessReportOut
from app.api.deps import get_current_user, get_user_dataset_version
from app.core.storage import storage_service
from app.engine.ml_engine import MLReadinessEngine

router = APIRouter(prefix="/datasets", tags=["ML Readiness"])

@router.post("/{dataset_id}/readiness", response_model=MLReadinessReportOut, status_code=status.HTTP_201_CREATED)
def evaluate_ml_readiness(
    dataset_id: str,
    req: MLReadinessRequest = MLReadinessRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, version = get_user_dataset_version(dataset_id, req.version_id, db, current_user)

    file_bytes = storage_service.get_file_bytes(version.storage_path)
    df = pl.read_parquet(file_bytes)

    eval_result = MLReadinessEngine.evaluate(
        df=df,
        task_type=req.task_type,
        target_column=req.target_column
    )

    report = MLReadinessReport(
        id=str(uuid.uuid4()),
        dataset_id=dataset.id,
        version_id=version.id,
        task_type=req.task_type,
        target_column=req.target_column,
        readiness_score=eval_result["readiness_score"],
        overall_status=eval_result["overall_status"],
        findings=eval_result["findings"],
        recommendations=eval_result["recommendations"],
        unresolved_issues=eval_result["unresolved_issues"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report

@router.get("/{dataset_id}/readiness", response_model=MLReadinessReportOut)
def get_ml_readiness(
    dataset_id: str,
    version_id: Optional[str] = Query(None),
    task_type: str = Query("classification"),
    target_column: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, version = get_user_dataset_version(dataset_id, version_id, db, current_user)
    report = db.query(MLReadinessReport).filter(
        MLReadinessReport.dataset_id == dataset.id,
        MLReadinessReport.version_id == version.id
    ).order_by(desc(MLReadinessReport.created_at)).first()

    if not report:
        return evaluate_ml_readiness(
            dataset_id,
            MLReadinessRequest(version_id=version.id, task_type=task_type, target_column=target_column),
            db,
            current_user
        )
    return report
