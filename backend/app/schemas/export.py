from pydantic import BaseModel
from typing import Optional, List

class ExportRequest(BaseModel):
    version_id: Optional[str] = None
    format: str = "csv" # "csv", "parquet", "json", "xlsx"
    columns: Optional[List[str]] = None
    compression: Optional[str] = None # None, "gzip", "snappy"
    include_header: bool = True

class ExportResponse(BaseModel):
    dataset_id: str
    version_id: str
    format: str
    filename: str
    file_size_bytes: int
    row_count: int
    column_count: int
    download_url: str
