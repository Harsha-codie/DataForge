from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class VersionOut(BaseModel):
    id: str
    dataset_id: str
    version_number: int
    branch_name: str
    parent_version_id: Optional[str] = None
    storage_path: str
    file_checksum: Optional[str] = None
    file_format: str
    row_count: int
    column_count: int
    schema_metadata: Optional[Dict[str, Any]] = None
    transformation_operation: str
    transformation_params: Optional[Dict[str, Any]] = None
    execution_status: str
    created_at: datetime
    created_by_user_id: Optional[str] = None

    class Config:
        from_attributes = True

class VersionCompareResponse(BaseModel):
    source_version_id: str
    source_version_number: int
    target_version_id: str
    target_version_number: int
    row_count_diff: int
    column_count_diff: int
    columns_added: List[str] = []
    columns_removed: List[str] = []
    columns_modified: List[Dict[str, Any]] = [] # [{name, old_type, new_type}]
    null_count_diffs: Dict[str, Dict[str, Any]] = {} # {col: {old_nulls, new_nulls, diff}}
    summary: str

class VersionRestoreRequest(BaseModel):
    target_version_id: str
    new_branch_name: Optional[str] = None

class BranchCreateRequest(BaseModel):
    source_version_id: str
    branch_name: str
