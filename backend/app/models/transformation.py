from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class TransformationRun(Base):
    __tablename__ = "transformation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    source_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    target_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    
    operation = Column(String(128), nullable=False)
    parameters = Column(JSON, nullable=False, default=dict)
    status = Column(String(32), nullable=False, default="completed") # started, completed, failed
    summary = Column(JSON, nullable=True) # rows_before, rows_after, columns_affected, etc.
    error_message = Column(Text, nullable=True)
    
    executed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="transformations")
    source_version = relationship("DatasetVersion", foreign_keys=[source_version_id])
    target_version = relationship("DatasetVersion", foreign_keys=[target_version_id])
