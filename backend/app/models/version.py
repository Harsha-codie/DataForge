from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    branch_name = Column(String(64), nullable=False, default="main")
    parent_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    
    storage_path = Column(String(512), nullable=False)
    file_checksum = Column(String(64), nullable=True) # SHA-256
    file_format = Column(String(32), nullable=False, default="parquet")
    row_count = Column(Integer, nullable=False, default=0)
    column_count = Column(Integer, nullable=False, default=0)
    
    schema_metadata = Column(JSON, nullable=True) # Column names, types, nullability
    transformation_operation = Column(String(128), nullable=False, default="upload")
    transformation_params = Column(JSON, nullable=True)
    
    execution_status = Column(String(32), nullable=False, default="ready") # ready, pending, failed
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("Dataset", back_populates="versions", foreign_keys=[dataset_id])
    parent_version = relationship("DatasetVersion", remote_side=[id], backref="child_versions")
    validation_reports = relationship("ValidationReport", back_populates="version", cascade="all, delete-orphan")
    ml_reports = relationship("MLReadinessReport", back_populates="version", cascade="all, delete-orphan")
