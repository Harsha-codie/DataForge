from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class TransformationPreviewRequest(BaseModel):
    dataset_id: str
    version_id: Optional[str] = None
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class TransformationPreviewResponse(BaseModel):
    operation: str
    parameters: Dict[str, Any]
    rows_before: int
    rows_after: int
    columns_before: int
    columns_after: int
    affected_row_count: int
    affected_column_count: int
    is_potentially_destructive: bool
    destruction_warnings: List[str] = []
    columns_added: List[str] = []
    columns_removed: List[str] = []
    sample_preview_before: List[Dict[str, Any]] = []
    sample_preview_after: List[Dict[str, Any]] = []
    validation_passed: bool
    validation_message: Optional[str] = None
    details: Dict[str, Any] = {}

class TransformationExecuteRequest(BaseModel):
    dataset_id: str
    version_id: Optional[str] = None
    operation: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    branch_name: Optional[str] = None

class TransformationHistoryItem(BaseModel):
    id: str
    dataset_id: str
    source_version_id: Optional[str] = None
    target_version_id: Optional[str] = None
    operation: str
    parameters: Dict[str, Any]
    status: str
    summary: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
