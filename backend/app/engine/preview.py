from typing import Dict, Any, List, Optional
import polars as pl
from app.engine.transformer import DataTransformer

class TransformationPreviewEngine:
    @classmethod
    def preview(cls, df: pl.DataFrame, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        rows_before = df.height
        cols_before = df.width
        columns_before_list = df.columns

        # Take a sample for fast preview
        sample_before = df.head(5).to_dicts()

        # Execute transformation on dataframe clone
        try:
            transformed_df, summary = DataTransformer.apply_transformation(df.clone(), operation, params)
            details = summary.get("details", {})
            validation_passed = True
            validation_message = None
        except Exception as e:
            return {
                "operation": operation,
                "parameters": params,
                "rows_before": rows_before,
                "rows_after": rows_before,
                "columns_before": cols_before,
                "columns_after": cols_before,
                "affected_row_count": 0,
                "affected_column_count": 0,
                "is_potentially_destructive": True,
                "destruction_warnings": [f"Transformation failed: {str(e)}"],
                "columns_added": [],
                "columns_removed": [],
                "sample_preview_before": sample_before,
                "sample_preview_after": [],
                "validation_passed": False,
                "validation_message": str(e),
                "details": {}
            }

        rows_after = transformed_df.height
        cols_after = transformed_df.width
        columns_after_list = transformed_df.columns

        columns_added = [c for c in columns_after_list if c not in columns_before_list]
        columns_removed = [c for c in columns_before_list if c not in columns_after_list]

        affected_rows = abs(rows_before - rows_after)
        affected_cols = abs(cols_before - cols_after)

        # Destructive checks
        destruction_warnings: List[str] = []
        is_destructive = False

        if rows_after == 0:
            is_destructive = True
            destruction_warnings.append("Destructive: Operation results in an empty dataset (0 rows remaining)!")
            validation_passed = False
            validation_message = "Operation drops 100% of rows."
        elif (rows_before - rows_after) > (0.25 * rows_before) and (rows_before - rows_after) > 0:
            is_destructive = True
            destruction_warnings.append(f"High data loss: removes {rows_before - rows_after} rows ({round((rows_before - rows_after)/rows_before * 100, 1)}% of dataset).")

        if len(columns_removed) > 0:
            is_destructive = True
            destruction_warnings.append(f"Permanent column removal: {columns_removed}")

        if operation == "cast_type":
            col = params.get("column")
            if col in transformed_df.columns:
                nulls_before = df[col].null_count()
                nulls_after = transformed_df[col].null_count()
                new_nulls = nulls_after - nulls_before
                if new_nulls > 0:
                    is_destructive = True
                    destruction_warnings.append(f"Type cast caused {new_nulls} invalid values to become NULL.")

        sample_after = transformed_df.head(5).to_dicts()

        return {
            "operation": operation,
            "parameters": params,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "columns_before": cols_before,
            "columns_after": cols_after,
            "affected_row_count": affected_rows,
            "affected_column_count": affected_cols,
            "is_potentially_destructive": is_destructive,
            "destruction_warnings": destruction_warnings,
            "columns_added": columns_added,
            "columns_removed": columns_removed,
            "sample_preview_before": sample_before,
            "sample_preview_after": sample_after,
            "validation_passed": validation_passed,
            "validation_message": validation_message,
            "details": details
        }
