from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class HistogramBin(BaseModel):
    bin_start: float
    bin_end: float
    count: int

class ValueFrequency(BaseModel):
    value: str
    count: int
    percentage: float

class NumericalColumnProfile(BaseModel):
    column: str
    inferred_type: str
    count: int
    missing_count: int
    missing_percentage: float
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    iqr: Optional[float] = None
    outlier_count: int = 0
    outlier_percentage: float = 0.0
    outlier_samples: List[float] = []
    histogram: List[HistogramBin] = []
    is_constant: bool = False

class CategoricalColumnProfile(BaseModel):
    column: str
    inferred_type: str
    count: int
    missing_count: int
    missing_percentage: float
    unique_count: int
    cardinality_ratio: float
    top_values: List[ValueFrequency] = []
    is_constant: bool = False

class DateColumnProfile(BaseModel):
    column: str
    inferred_type: str
    count: int
    missing_count: int
    missing_percentage: float
    valid_date_count: int
    invalid_date_count: int
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    date_warnings: List[str] = []

class QualityIssue(BaseModel):
    code: str
    severity: str # "info", "warning", "critical"
    column: Optional[str] = None
    title: str
    description: str
    affected_rows: int
    sample_values: List[Any] = []
    suggested_action: str

class ProfilingReport(BaseModel):
    dataset_id: str
    version_id: str
    version_number: int
    row_count: int
    column_count: int
    file_size_bytes: int
    duplicate_row_count: int
    duplicate_row_percentage: float
    total_missing_values: int
    total_missing_percentage: float
    is_sampled: bool = False
    sample_size: Optional[int] = None
    columns: List[str]
    column_types: Dict[str, str]
    numerical_profiles: Dict[str, NumericalColumnProfile] = {}
    categorical_profiles: Dict[str, CategoricalColumnProfile] = {}
    date_profiles: Dict[str, DateColumnProfile] = {}
    quality_issues: List[QualityIssue] = []
    overall_health_score: float # 0 to 100
