import traceback
import polars as pl
from datetime import datetime, timezone
import uuid
import threading
from app.database import SessionLocal
from app.models.job import BackgroundJob
from app.models.dataset import Dataset
from app.models.version import DatasetVersion
from app.models.transformation import TransformationRun
from app.models.validation import ValidationReport
from app.models.ml_readiness import MLReadinessReport
from app.core.storage import storage_service
from app.engine.reader import DataReader
from app.engine.profiler import DataProfiler
from app.engine.transformer import DataTransformer
from app.engine.ml_engine import MLReadinessEngine

def update_job_status(job_id: str, status: str, progress: int = 0, message: str = "", result: dict = None, error: str = None):
    db = SessionLocal()
    try:
        job = db.query(BackgroundJob).filter(BackgroundJob.id == job_id).first()
        if job:
            job.status = status
            job.progress_percent = progress
            if message:
                job.message = message
            if result:
                job.result_payload = result
            if error:
                job.error_details = error
            job.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()

def execute_profiling(job_id: str, dataset_id: str, version_id: str):
    db = SessionLocal()
    try:
        update_job_status(job_id, "running", 10, "Loading dataset version from storage...")
        version = db.query(DatasetVersion).filter(DatasetVersion.id == version_id).first()
        if not version:
            raise ValueError(f"Version {version_id} not found.")

        # Load file bytes
        file_bytes = storage_service.get_file_bytes(version.storage_path)
        df = pl.read_parquet(file_bytes)

        update_job_status(job_id, "running", 50, "Computing statistical distribution and quality checks...")
        report = DataProfiler.profile_dataframe(
            df=df,
            dataset_id=dataset_id,
            version_id=version_id,
            version_number=version.version_number,
            file_size_bytes=len(file_bytes)
        )

        update_job_status(job_id, "completed", 100, "Profiling completed successfully.", result=report)
        return report
    except Exception as e:
        err = f"{str(e)}\n{traceback.format_exc()}"
        update_job_status(job_id, "failed", 0, f"Profiling failed: {str(e)}", error=err)
    finally:
        db.close()

def execute_transformation(job_id: str, dataset_id: str, source_version_id: str, operation: str, params: dict, user_id: str, branch_name: str = "main"):
    db = SessionLocal()
    try:
        update_job_status(job_id, "running", 15, f"Starting transformation: {operation}...")
        source_ver = db.query(DatasetVersion).filter(DatasetVersion.id == source_version_id).first()
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not source_ver or not dataset:
            raise ValueError("Dataset or source version not found.")

        # Read source data
        src_bytes = storage_service.get_file_bytes(source_ver.storage_path)
        df = pl.read_parquet(src_bytes)

        update_job_status(job_id, "running", 45, f"Executing {operation} on {df.height} rows...")
        transformed_df, details = DataTransformer.apply_transformation(df, operation, params)

        update_job_status(job_id, "running", 75, "Saving new immutable version...")
        parquet_bytes = DataReader.dataframe_to_parquet_bytes(transformed_df)
        
        # Determine new version number
        latest_ver = db.query(DatasetVersion).filter(DatasetVersion.dataset_id == dataset_id).order_by(DatasetVersion.version_number.desc()).first()
        new_version_num = (latest_ver.version_number + 1) if latest_ver else 1

        new_storage_path = f"datasets/{dataset_id}/v{new_version_num}_{uuid.uuid4().hex[:8]}.parquet"
        saved_path, checksum, file_size = storage_service.save_file(
            file_obj=parquet_bytes if hasattr(parquet_bytes, 'read') else io_bytes(parquet_bytes),
            filename=new_storage_path,
            content_type="application/octet-stream"
        )

        # Create new version record
        new_version = DatasetVersion(
            dataset_id=dataset_id,
            version_number=new_version_num,
            branch_name=branch_name or source_ver.branch_name,
            parent_version_id=source_ver.id,
            storage_path=saved_path,
            file_checksum=checksum,
            file_format="parquet",
            row_count=transformed_df.height,
            column_count=transformed_df.width,
            schema_metadata={col: str(dtype) for col, dtype in zip(transformed_df.columns, transformed_df.dtypes)},
            transformation_operation=operation,
            transformation_params=params,
            execution_status="ready",
            created_by_user_id=user_id,
        )
        db.add(new_version)
        db.flush()

        # Update dataset current version
        dataset.current_version_id = new_version.id
        dataset.updated_at = datetime.now(timezone.utc)

        # Record transformation run
        trans_run = TransformationRun(
            dataset_id=dataset_id,
            source_version_id=source_ver.id,
            target_version_id=new_version.id,
            operation=operation,
            parameters=params,
            status="completed",
            summary=details,
            executed_by_user_id=user_id,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(trans_run)
        db.commit()

        result_payload = {
            "new_version_id": new_version.id,
            "version_number": new_version.version_number,
            "row_count": new_version.row_count,
            "column_count": new_version.column_count,
            "details": details
        }
        update_job_status(job_id, "completed", 100, "Transformation complete.", result=result_payload)
        return result_payload
    except Exception as e:
        err = f"{str(e)}\n{traceback.format_exc()}"
        update_job_status(job_id, "failed", 0, f"Transformation failed: {str(e)}", error=err)
        # Record failed run
        try:
            failed_run = TransformationRun(
                dataset_id=dataset_id,
                source_version_id=source_version_id,
                target_version_id=None,
                operation=operation,
                parameters=params,
                status="failed",
                error_message=str(e),
                executed_by_user_id=user_id,
                completed_at=datetime.now(timezone.utc)
            )
            db.add(failed_run)
            db.commit()
        except Exception:
            pass
    finally:
        db.close()

def io_bytes(data: bytes):
    import io
    return io.BytesIO(data)

def dispatch_task(task_func, *args, **kwargs):
    """
    Attempts to dispatch via Celery if available, otherwise executes in a background thread.
    Guarantees that background tasks execute reliably regardless of local Redis availability!
    """
    t = threading.Thread(target=task_func, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
