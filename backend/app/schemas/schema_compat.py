from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExpectedColumn(BaseModel):
    name: str
    data_type: str # integer, float, string, boolean, date
    required: bool = True
    nullable: bool = True
    allowed_values: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    regex_pattern: Optional[str] = None

class SchemaDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: Optional[str] = None
    columns: List[ExpectedColumn]

class SchemaDefinitionOut(BaseModel):
    id: str
    user_id: str
    dataset_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    columns: List[ExpectedColumn]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SchemaMismatchIssue(BaseModel):
    column: str
    severity: str # "warning", "critical"
    issue_type: str # "missing_column", "type_mismatch", "mixed_type", "nullability_violation", "constraint_violation", "enum_violation"
    message: str
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    affected_rows: int = 0
    sample_values: List[Any] = []
    suggested_action: str

class ColumnCompatibilityDetail(BaseModel):
    name: str
    status: str # "matched", "type_mismatch", "constraint_violation", "missing", "unexpected"
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    incompatible_count: int = 0
    null_violations: int = 0
    sample_invalid_values: List[Any] = []

class SchemaCompatibilityReport(BaseModel):
    dataset_id: str
    version_id: str
    schema_id: Optional[str] = None
    compatibility_status: str # "compatible", "warnings", "incompatible"
    total_expected_columns: int
    matched_columns_count: int
    missing_columns: List[str] = []
    unexpected_columns: List[str] = []
    issues: List[SchemaMismatchIssue] = []
    column_details: List[ColumnCompatibilityDetail] = []
    created_at: datetime
