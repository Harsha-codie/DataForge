from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ValidationReport(Base):
    __tablename__ = "validation_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    overall_status = Column(String(32), nullable=False) # passed, warning, failed
    rules_checked = Column(JSON, nullable=False, default=list)
    violations_count = Column(Integer, nullable=False, default=0)
    issues = Column(JSON, nullable=False, default=list) # [{rule, column, severity, message, row_count, sample_values}]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("Dataset", back_populates="validations")
    version = relationship("DatasetVersion", back_populates="validation_reports")
