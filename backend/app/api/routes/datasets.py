import io
import os
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import polars as pl
from app.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.version import DatasetVersion
from app.schemas.dataset import DatasetOut, DatasetListItem, DatasetPreviewResponse
from app.api.deps import get_current_user, get_user_dataset, get_user_dataset_version
from app.core.storage import storage_service
from app.engine.reader import DataReader
from app.config import settings

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def _cleanup_storage_paths(storage_paths: List[str]) -> None:
    for storage_path in storage_paths:
        try:
            if storage_service.exists(storage_path) and not storage_service.delete_file(storage_path):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Dataset storage cleanup is incomplete; retry deletion.",
                )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Dataset storage cleanup failed: {exc}",
            ) from exc

@router.post("/upload", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate filename and format
    filename = (file.filename or "uploaded_dataset.csv").replace("\\", "/").rsplit("/", 1)[-1]
    if not filename:
        filename = "uploaded_dataset.csv"
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in ("csv", "parquet", "json", "xlsx", "xls", "txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: .{ext}. Supported formats are CSV, Parquet, JSON, and XLSX."
        )

    # Read uploaded bytes
    content = await file.read()
    if not content or len(content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # Parse dataset with Polars engine
    try:
        df = DataReader.read_to_polars(content, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse dataset: {str(e)}"
        )

    dataset_id = str(uuid.uuid4())
    version_id = str(uuid.uuid4())
    dataset_name = name.strip() if name and name.strip() else os.path.splitext(filename)[0]

    # 1. Store original raw file immutably
    raw_storage_path = f"raw/{dataset_id}/{filename}"
    storage_service.save_file(
        file_obj=io.BytesIO(content),
        filename=raw_storage_path,
        content_type=file.content_type
    )

    # 2. Store internal canonical Parquet for Version 1
    parquet_bytes = DataReader.dataframe_to_parquet_bytes(df)
    v1_storage_path = f"datasets/{dataset_id}/v1_{uuid.uuid4().hex[:8]}.parquet"
    saved_v1_path, v1_checksum, v1_size = storage_service.save_file(
        file_obj=io.BytesIO(parquet_bytes),
        filename=v1_storage_path,
        content_type="application/octet-stream"
    )

    metadata = DataReader.extract_metadata(df)

    # 3. Create Dataset record
    dataset = Dataset(
        id=dataset_id,
        user_id=current_user.id,
        name=dataset_name,
        description=description,
        original_filename=filename,
        format=ext if ext != "txt" else "csv",
        file_size_bytes=len(content),
        current_version_id=version_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(dataset)

    # 4. Create Version 1 record
    version_1 = DatasetVersion(
        id=version_id,
        dataset_id=dataset_id,
        version_number=1,
        branch_name="main",
        parent_version_id=None,
        storage_path=saved_v1_path,
        file_checksum=v1_checksum,
        file_format="parquet",
        row_count=df.height,
        column_count=df.width,
        schema_metadata=metadata["schema"],
        transformation_operation="upload",
        transformation_params={"original_filename": filename, "file_size_bytes": len(content)},
        execution_status="ready",
        created_by_user_id=current_user.id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(version_1)
    db.commit()
    db.refresh(dataset)
    db.refresh(version_1)

    return dataset

@router.get("/", response_model=List[DatasetListItem])
def list_datasets(
    search: Optional[str] = Query(None),
    sort_by: str = Query("updated_at", regex="^(created_at|updated_at|name|file_size_bytes)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dataset).filter(Dataset.user_id == current_user.id)
    if search:
        query = query.filter(Dataset.name.ilike(f"%{search}%"))

    order_col = getattr(Dataset, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    datasets = query.all()
    results = []
    for d in datasets:
        curr_ver = db.query(DatasetVersion).filter(DatasetVersion.id == d.current_version_id).first()
        results.append(DatasetListItem(
            id=d.id,
            name=d.name,
            description=d.description,
            original_filename=d.original_filename,
            format=d.format,
            file_size_bytes=d.file_size_bytes,
            current_version_id=d.current_version_id,
            row_count=curr_ver.row_count if curr_ver else 0,
            column_count=curr_ver.column_count if curr_ver else 0,
            version_number=curr_ver.version_number if curr_ver else 1,
            created_at=d.created_at,
            updated_at=d.updated_at
        ))
    return results

@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset = get_user_dataset(dataset_id, db, current_user)
    curr_ver = db.query(DatasetVersion).filter(DatasetVersion.id == dataset.current_version_id).first()
    res = DatasetOut.model_validate(dataset)
    if curr_ver:
        res.current_version = curr_ver
    return res

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset = get_user_dataset(dataset_id, db, current_user)
    storage_paths = []
    versions = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == dataset.id).all()
    for v in versions:
        storage_paths.append(v.storage_path)

    if dataset.original_filename:
        storage_paths.append(f"raw/{dataset.id}/{dataset.original_filename}")

    # Keep the database record when storage cleanup fails so deletion can be retried.
    _cleanup_storage_paths(storage_paths)

    db.delete(dataset)
    db.commit()
    return None

@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview(
    dataset_id: str,
    version_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dataset, version = get_user_dataset_version(dataset_id, version_id, db, current_user)
    
    file_bytes = storage_service.get_file_bytes(version.storage_path)
    df = pl.read_parquet(file_bytes)

    offset = (page - 1) * page_size
    sliced_df = df.slice(offset, page_size)
    rows = sliced_df.to_dicts()

    col_types = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}

    return DatasetPreviewResponse(
        dataset_id=dataset.id,
        version_id=version.id,
        version_number=version.version_number,
        total_rows=df.height,
        total_columns=df.width,
        columns=df.columns,
        column_types=col_types,
        page=page,
        page_size=page_size,
        rows=rows
    )
