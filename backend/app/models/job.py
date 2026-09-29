from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=True, index=True)
    
    job_type = Column(String(64), nullable=False) # profile, transform, export, ml_readiness, schema_check
    status = Column(String(32), nullable=False, default="queued") # queued, running, completed, failed, cancelled
    progress_percent = Column(Integer, nullable=False, default=0)
    message = Column(String(255), nullable=True)
    result_payload = Column(JSON, nullable=True)
    error_details = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="jobs")
    dataset = relationship("Dataset", back_populates="jobs")
