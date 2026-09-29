from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("BackgroundJob", back_populates="user", cascade="all, delete-orphan")
    schemas = relationship("DatasetSchema", back_populates="user", cascade="all, delete-orphan")
