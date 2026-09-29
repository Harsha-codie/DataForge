from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class MLReadinessReport(Base):
    __tablename__ = "ml_readiness_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    task_type = Column(String(64), nullable=False) # classification, regression, etc.
    target_column = Column(String(255), nullable=True)
    readiness_score = Column(Float, nullable=False, default=0.0) # 0 to 100
    overall_status = Column(String(32), nullable=False) # ready, needs_attention, not_ready
    
    findings = Column(JSON, nullable=False, default=list) # [{category, severity, issue, explanation, rows_affected}]
    recommendations = Column(JSON, nullable=False, default=list) # [{step, description, action_type}]
    unresolved_issues = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("Dataset", back_populates="ml_reports")
    version = relationship("DatasetVersion", back_populates="ml_reports")
