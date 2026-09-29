from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ValidationIssue(BaseModel):
    rule: str
    severity: str # "critical", "warning", "info"
    column: Optional[str] = None
    message: str
    row_count: int = 0
    sample_values: List[Any] = []

class ValidationReportOut(BaseModel):
    id: str
    dataset_id: str
    version_id: str
    overall_status: str # "passed", "warning", "failed"
    rules_checked: List[str]
    violations_count: int
    issues: List[ValidationIssue]
    created_at: datetime

    class Config:
        from_attributes = True

class ValidateRequest(BaseModel):
    version_id: Optional[str] = None
    custom_rules: Optional[Dict[str, Any]] = None
