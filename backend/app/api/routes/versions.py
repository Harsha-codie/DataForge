import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import polars as pl
from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.version import DatasetVersion
from app.schemas.version import (
    VersionOut,
    VersionCompareResponse,
    VersionRestoreRequest,
    BranchCreateRequest
)
from app.api.deps import get_current_user, get_user_dataset, get_user_dataset_version
from app.core.storage import storage_service

router = APIRouter(prefix="/datasets", tags=["Versions"])

@router.get("/{dataset_id}/versions", response_model=List[VersionOut])
def list_versions(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset = get_user_dataset(dataset_id, db, current_user)
    versions = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset.id
    ).order_by(desc(DatasetVersion.version_number)).all()
    return versions

@router.get("/{dataset_id}/versions/{version_id}", response_model=VersionOut)
def get_version(
    dataset_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, version = get_user_dataset_version(dataset_id, version_id, db, current_user)
    return version

@router.post("/{dataset_id}/versions/compare", response_model=VersionCompareResponse)
def compare_versions(
    dataset_id: str,
    source_version_id: str = Query(...),
    target_version_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset = get_user_dataset(dataset_id, db, current_user)
    v1 = db.query(DatasetVersion).filter(DatasetVersion.id == source_version_id, DatasetVersion.dataset_id == dataset.id).first()
    v2 = db.query(DatasetVersion).filter(DatasetVersion.id == target_version_id, DatasetVersion.dataset_id == dataset.id).first()

    if not v1 or not v2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both versions not found.")

    b1 = storage_service.get_file_bytes(v1.storage_path)
    b2 = storage_service.get_file_bytes(v2.storage_path)

    df1 = pl.read_parquet(b1)
    df2 = pl.read_parquet(b2)

    cols1 = set(df1.columns)
    cols2 = set(df2.columns)

    added = sorted(list(cols2 - cols1))
    removed = sorted(list(cols1 - cols2))
    common = sorted(list(cols1 & cols2))

    modified = []
    for c in common:
        t1 = str(df1[c].dtype)
        t2 = str(df2[c].dtype)
        if t1 != t2:
            modified.append({"name": c, "old_type": t1, "new_type": t2})

    null_diffs = {}
    for c in common:
        n1 = df1[c].null_count()
        n2 = df2[c].null_count()
        if n1 != n2:
            null_diffs[c] = {
                "old_nulls": n1,
                "new_nulls": n2,
                "diff": n2 - n1
            }

    row_diff = df2.height - df1.height
    col_diff = df2.width - df1.width

    summary = (
        f"Compared Version {v1.version_number} -> Version {v2.version_number}. "
        f"Rows change: {row_diff:+d} ({df1.height} -> {df2.height}). "
        f"Columns change: {col_diff:+d} ({df1.width} -> {df2.width}). "
        f"{len(added)} added, {len(removed)} removed, {len(modified)} type changes."
    )

    return VersionCompareResponse(
        source_version_id=v1.id,
        source_version_number=v1.version_number,
        target_version_id=v2.id,
        target_version_number=v2.version_number,
        row_count_diff=row_diff,
        column_count_diff=col_diff,
        columns_added=added,
        columns_removed=removed,
        columns_modified=modified,
        null_count_diffs=null_diffs,
        summary=summary
    )

@router.post("/{dataset_id}/versions/restore", response_model=VersionOut)
def restore_version(
    dataset_id: str,
    req: VersionRestoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, target_version = get_user_dataset_version(dataset_id, req.target_version_id, db, current_user)

    # Set as active current version (does NOT delete any newer versions)
    dataset.current_version_id = target_version.id
    dataset.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(dataset)
    db.refresh(target_version)

    return target_version

@router.post("/{dataset_id}/versions/branch", response_model=VersionOut, status_code=status.HTTP_201_CREATED)
def create_branch(
    dataset_id: str,
    req: BranchCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, source_ver = get_user_dataset_version(dataset_id, req.source_version_id, db, current_user)

    # Copy file reference to branch version
    latest_ver = db.query(DatasetVersion).filter(
        DatasetVersion.dataset_id == dataset.id
    ).order_by(DatasetVersion.version_number.desc()).first()
    new_version_num = (latest_ver.version_number + 1) if latest_ver else 1

    new_branch_ver = DatasetVersion(
        id=str(uuid.uuid4()),
        dataset_id=dataset.id,
        version_number=new_version_num,
        branch_name=req.branch_name,
        parent_version_id=source_ver.id,
        storage_path=source_ver.storage_path, # immutable reference
        file_checksum=source_ver.file_checksum,
        file_format=source_ver.file_format,
        row_count=source_ver.row_count,
        column_count=source_ver.column_count,
        schema_metadata=source_ver.schema_metadata,
        transformation_operation="branch",
        transformation_params={"source_version_number": source_ver.version_number, "branch_name": req.branch_name},
        execution_status="ready",
        created_by_user_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_branch_ver)
    dataset.current_version_id = new_branch_ver.id
    dataset.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(new_branch_ver)

    return new_branch_ver
