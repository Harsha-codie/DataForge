from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobStatusResponse(BaseModel):
    id: str
    user_id: str
    dataset_id: Optional[str] = None
    job_type: str
    status: str # queued, running, completed, failed, cancelled
    progress_percent: int
    message: Optional[str] = None
    result_payload: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
