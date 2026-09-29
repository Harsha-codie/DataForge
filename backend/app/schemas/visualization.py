from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class VisualizationType(str, Enum):
    histogram = "histogram"
    kde = "kde"
    box = "box"
    bar = "bar"
    violin = "violin"
    scatter = "scatter"
    correlation_heatmap = "correlation_heatmap"
    pair_plot = "pair_plot"
    line = "line"
    grouped_box = "grouped_box"
    missing_bar = "missing_bar"
    missing_heatmap = "missing_heatmap"
    outlier = "outlier"
    class_distribution = "class_distribution"


class VisualizationRequest(BaseModel):
    chart_type: VisualizationType
    columns: List[str] = Field(default_factory=list, max_length=8)
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    group_column: Optional[str] = None
    bins: int = Field(default=20, ge=5, le=100)
    correlation_method: str = Field(default="pearson")
    sample_size: int = Field(default=5000, ge=100, le=20000)

    @field_validator("correlation_method")
    @classmethod
    def validate_correlation_method(cls, value: str) -> str:
        if value not in {"pearson", "spearman"}:
            raise ValueError("correlation_method must be pearson or spearman")
        return value


class VisualizationMetadata(BaseModel):
    dataset_id: str
    version_id: str
    version_number: int
    row_count: int
    columns: List[str]
    column_types: Dict[str, str]
    numeric_columns: List[str]
    categorical_columns: List[str]
    date_columns: List[str]
    missing_columns: List[str]
    recommendations: List[Dict[str, Any]]


class VisualizationResponse(BaseModel):
    chart_type: VisualizationType
    title: str
    data: Any
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
