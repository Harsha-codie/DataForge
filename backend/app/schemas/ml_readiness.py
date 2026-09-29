from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class MLReadinessRequest(BaseModel):
    version_id: Optional[str] = None
    task_type: str = "classification" # classification, regression, clustering
    target_column: Optional[str] = None

class MLReadinessFinding(BaseModel):
    category: str # target_quality, feature_types, missing_data, cardinality, outliers, leakage
    severity: str # critical, warning, info
    issue: str
    explanation: str
    rows_affected: int = 0
    sample_values: List[Any] = []
    recommended_operation: Optional[str] = None

class MLRecommendation(BaseModel):
    step: int
    category: str
    title: str
    description: str
    suggested_operation: str
    suggested_params: Dict[str, Any] = {}

class MLReadinessReportOut(BaseModel):
    id: str
    dataset_id: str
    version_id: str
    task_type: str
    target_column: Optional[str] = None
    readiness_score: float # 0 to 100
    overall_status: str # ready, needs_attention, not_ready
    findings: List[MLReadinessFinding]
    recommendations: List[MLRecommendation]
    unresolved_issues: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class MLTrainTestSplitRequest(BaseModel):
    version_id: Optional[str] = None
    target_column: Optional[str] = None
    test_size: float = 0.2
    validation_size: float = 0.0
    random_state: int = 42
    stratify: bool = False
