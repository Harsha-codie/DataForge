import io
import os
from typing import Tuple, Dict, Any, Optional
import chardet
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

class DataReader:
    @staticmethod
    def detect_encoding(file_bytes: bytes) -> str:
        sample = file_bytes[:65536]
        result = chardet.detect(sample)
        encoding = result.get("encoding") or "utf-8"
        # Common fallback
        if encoding.lower() in ("ascii", "windows-1252", "iso-8859-1"):
            # Check if valid utf-8
            try:
                sample.decode("utf-8")
                return "utf-8"
            except UnicodeDecodeError:
                return encoding
        return encoding

    @classmethod
    def read_to_polars(cls, file_bytes: bytes, filename: str) -> pl.DataFrame:
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise ValueError("Uploaded file is empty.")

        ext = os.path.splitext(filename)[1].lower().lstrip(".")
        if ext in ("csv", "txt"):
            encoding = cls.detect_encoding(file_bytes)
            try:
                # Try reading with Polars directly
                df = pl.read_csv(
                    io.BytesIO(file_bytes),
                    encoding=encoding,
                    ignore_errors=False,
                    infer_schema_length=10000,
                    null_values=["", "NA", "N/A", "null", "NULL", "None", "nan", "NaN"]
                )
            except Exception:
                # Fallback to permissive reading
                try:
                    df = pl.read_csv(
                        io.BytesIO(file_bytes),
                        encoding=encoding,
                        ignore_errors=True,
                        null_values=["", "NA", "N/A", "null", "NULL", "None", "nan", "NaN"]
                    )
                except Exception as ex:
                    raise ValueError(f"Malformed CSV file: {str(ex)}")

        elif ext == "parquet":
            try:
                df = pl.read_parquet(io.BytesIO(file_bytes))
            except Exception as ex:
                raise ValueError(f"Malformed Parquet file: {str(ex)}")

        elif ext == "json":
            try:
                # Try standard json or ndjson
                try:
                    df = pl.read_json(io.BytesIO(file_bytes))
                except Exception:
                    df = pl.read_ndjson(io.BytesIO(file_bytes))
            except Exception as ex:
                raise ValueError(f"Malformed JSON file: {str(ex)}")

        elif ext in ("xlsx", "xls"):
            try:
                import pandas as pd
                pdf = pd.read_excel(io.BytesIO(file_bytes))
                df = pl.from_pandas(pdf)
            except Exception as ex:
                raise ValueError(f"Malformed Excel file: {str(ex)}")
        else:
            raise ValueError(f"Unsupported file format: .{ext}. Supported formats are CSV, Parquet, JSON, and XLSX.")

        if df.height == 0:
            raise ValueError("Dataset has 0 rows.")
        if df.width == 0:
            raise ValueError("Dataset has 0 columns.")

        return df

    @staticmethod
    def dataframe_to_parquet_bytes(df: pl.DataFrame) -> bytes:
        buf = io.BytesIO()
        df.write_parquet(buf, compression="snappy")
        return buf.getvalue()

    @staticmethod
    def extract_metadata(df: pl.DataFrame) -> Dict[str, Any]:
        return {
            "row_count": df.height,
            "column_count": df.width,
            "columns": df.columns,
            "schema": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
        }
