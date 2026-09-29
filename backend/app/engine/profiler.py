import math
from typing import Dict, Any, List, Optional
import polars as pl
import numpy as np

class DataProfiler:
    @classmethod
    def profile_dataframe(cls, df: pl.DataFrame, dataset_id: str, version_id: str, version_number: int, file_size_bytes: int = 0) -> Dict[str, Any]:
        row_count = df.height
        col_count = df.width
        columns = df.columns
        column_types = {col: str(dtype) for col, dtype in zip(columns, df.dtypes)}

        # 1. Duplicate rows
        try:
            duplicate_row_count = row_count - df.unique().height
        except Exception:
            duplicate_row_count = 0
        duplicate_percentage = round((duplicate_row_count / row_count * 100) if row_count > 0 else 0.0, 2)

        # 2. Missing values total
        null_counts = {col: df[col].null_count() for col in columns}
        total_missing = sum(null_counts.values())
        total_cells = row_count * col_count if (row_count * col_count) > 0 else 1
        total_missing_percentage = round((total_missing / total_cells * 100), 2)

        numerical_profiles: Dict[str, Any] = {}
        categorical_profiles: Dict[str, Any] = {}
        date_profiles: Dict[str, Any] = {}
        quality_issues: List[Dict[str, Any]] = []

        # Check for duplicate rows issue
        if duplicate_row_count > 0:
            quality_issues.append({
                "code": "DUPLICATE_ROWS",
                "severity": "warning" if duplicate_percentage < 15 else "critical",
                "column": None,
                "title": f"{duplicate_row_count} duplicate rows detected",
                "description": f"Found {duplicate_row_count} ({duplicate_percentage}%) exact duplicate rows across all columns.",
                "affected_rows": duplicate_row_count,
                "sample_values": [],
                "suggested_action": "Apply duplicate removal transformation to retain unique rows."
            })

        for col in columns:
            series = df[col]
            dtype = series.dtype
            missing = null_counts[col]
            missing_pct = round((missing / row_count * 100) if row_count > 0 else 0.0, 2)

            # High missingness warning
            if missing_pct > 30.0:
                quality_issues.append({
                    "code": "HIGH_MISSINGNESS",
                    "severity": "critical" if missing_pct > 60 else "warning",
                    "column": col,
                    "title": f"High missing values in '{col}' ({missing_pct}%)",
                    "description": f"Column '{col}' has {missing} missing values out of {row_count} rows.",
                    "affected_rows": missing,
                    "sample_values": [],
                    "suggested_action": "Impute with mean/median/constant or drop column if non-essential."
                })

            # Numerical profiling
            if dtype.is_numeric():
                non_null = series.drop_nulls()
                non_null_count = non_null.len()

                if non_null_count == 0:
                    num_prof = {
                        "column": col,
                        "inferred_type": str(dtype),
                        "count": row_count,
                        "missing_count": missing,
                        "missing_percentage": missing_pct,
                        "mean": None, "median": None, "std": None,
                        "min": None, "max": None, "q25": None, "q75": None,
                        "iqr": None, "outlier_count": 0, "outlier_percentage": 0.0,
                        "outlier_samples": [], "histogram": [], "is_constant": True
                    }
                else:
                    arr = non_null.to_numpy()
                    min_val = float(np.min(arr))
                    max_val = float(np.max(arr))
                    mean_val = float(np.mean(arr))
                    std_val = float(np.std(arr)) if len(arr) > 1 else 0.0
                    median_val = float(np.median(arr))
                    q25 = float(np.percentile(arr, 25))
                    q75 = float(np.percentile(arr, 75))
                    iqr = q75 - q25
                    is_const = (min_val == max_val)

                    # Outlier detection using 1.5 * IQR
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
                    outlier_count = int(len(outliers))
                    outlier_pct = round((outlier_count / non_null_count * 100), 2)
                    outlier_samples = [float(x) for x in outliers[:5]]

                    if outlier_count > 0:
                        quality_issues.append({
                            "code": "OUTLIERS_DETECTED",
                            "severity": "warning",
                            "column": col,
                            "title": f"Potential outliers in '{col}' ({outlier_count} values)",
                            "description": f"Identified {outlier_count} values outside 1.5x IQR [{round(lower_bound, 2)}, {round(upper_bound, 2)}].",
                            "affected_rows": outlier_count,
                            "sample_values": outlier_samples,
                            "suggested_action": "Inspect distribution and apply clipping or filtering if erroneous."
                        })

                    # 10-bin Histogram
                    hist_bins = []
                    if not is_const and non_null_count > 1:
                        counts, bin_edges = np.histogram(arr, bins=10)
                        for i in range(len(counts)):
                            hist_bins.append({
                                "bin_start": round(float(bin_edges[i]), 2),
                                "bin_end": round(float(bin_edges[i+1]), 2),
                                "count": int(counts[i])
                            })

                    num_prof = {
                        "column": col,
                        "inferred_type": str(dtype),
                        "count": row_count,
                        "missing_count": missing,
                        "missing_percentage": missing_pct,
                        "mean": round(mean_val, 2) if not math.isnan(mean_val) else None,
                        "median": round(median_val, 2) if not math.isnan(median_val) else None,
                        "std": round(std_val, 2) if not math.isnan(std_val) else None,
                        "min": round(min_val, 2) if not math.isnan(min_val) else None,
                        "max": round(max_val, 2) if not math.isnan(max_val) else None,
                        "q25": round(q25, 2) if not math.isnan(q25) else None,
                        "q75": round(q75, 2) if not math.isnan(q75) else None,
                        "iqr": round(iqr, 2) if not math.isnan(iqr) else None,
                        "outlier_count": outlier_count,
                        "outlier_percentage": outlier_pct,
                        "outlier_samples": outlier_samples,
                        "histogram": hist_bins,
                        "is_constant": is_const
                    }

                    if is_const:
                        quality_issues.append({
                            "code": "CONSTANT_COLUMN",
                            "severity": "warning",
                            "column": col,
                            "title": f"Constant column '{col}'",
                            "description": f"Column '{col}' has identical value ({min_val}) across all rows.",
                            "affected_rows": row_count,
                            "sample_values": [min_val],
                            "suggested_action": "Consider dropping constant column as it provides zero variance."
                        })

                numerical_profiles[col] = num_prof

            # Date / Datetime profiling
            elif dtype in (pl.Date, pl.Datetime):
                non_null = series.drop_nulls()
                min_d = str(non_null.min()) if non_null.len() > 0 else None
                max_d = str(non_null.max()) if non_null.len() > 0 else None
                date_profiles[col] = {
                    "column": col,
                    "inferred_type": str(dtype),
                    "count": row_count,
                    "missing_count": missing,
                    "missing_percentage": missing_pct,
                    "valid_date_count": non_null.len(),
                    "invalid_date_count": 0,
                    "min_date": min_d,
                    "max_date": max_d,
                    "date_warnings": []
                }

            # String / Categorical / Boolean profiling
            else:
                non_null = series.drop_nulls()
                str_list = [str(x) for x in non_null.to_list()]
                unique_vals, counts = np.unique(str_list, return_counts=True) if len(str_list) > 0 else ([], [])
                unique_count = len(unique_vals)
                cardinality_ratio = round((unique_count / row_count) if row_count > 0 else 0.0, 4)

                # Sort top 10 frequencies
                top_values = []
                if len(unique_vals) > 0:
                    sorted_indices = np.argsort(counts)[::-1]
                    for idx in sorted_indices[:10]:
                        val_str = str(unique_vals[idx])
                        cnt = int(counts[idx])
                        top_values.append({
                            "value": val_str,
                            "count": cnt,
                            "percentage": round((cnt / row_count * 100), 2)
                        })

                is_const = (unique_count == 1 and missing == 0)
                if is_const:
                    quality_issues.append({
                        "code": "CONSTANT_COLUMN",
                        "severity": "warning",
                        "column": col,
                        "title": f"Constant column '{col}'",
                        "description": f"Column '{col}' only contains one unique value: '{unique_vals[0]}'.",
                        "affected_rows": row_count,
                        "sample_values": [unique_vals[0]],
                        "suggested_action": "Drop column before ML model training."
                    })

                # Quality check: Mixed type detection (e.g. numbers stored in string column)
                numeric_looks = 0
                sample_dirty = []
                for val in str_list[:500]:
                    cleaned = val.replace("$", "").replace(",", "").replace("%", "").strip()
                    try:
                        float(cleaned)
                        numeric_looks += 1
                    except ValueError:
                        if val.lower() in ("unknown", "n/a", "none", "null", "?", "-"):
                            sample_dirty.append(val)

                if len(str_list) > 0 and (numeric_looks / min(len(str_list), 500)) > 0.6 and (numeric_looks < len(str_list[:500])):
                    quality_issues.append({
                        "code": "MIXED_DATA_TYPES",
                        "severity": "critical",
                        "column": col,
                        "title": f"Mixed data types in string column '{col}'",
                        "description": f"Column '{col}' contains numeric values alongside text representations ({sample_dirty[:3]}).",
                        "affected_rows": row_count - numeric_looks,
                        "sample_values": sample_dirty[:5],
                        "suggested_action": "Convert column to float/integer with invalid coercion to null."
                    })

                # Check if strings look like dates
                date_looks = 0
                for val in str_list[:100]:
                    if "-" in val or "/" in val:
                        parts = val.replace("/", "-").split("-")
                        if len(parts) == 3:
                            date_looks += 1
                if len(str_list) > 0 and (date_looks / min(len(str_list), 100)) > 0.7:
                    date_profiles[col] = {
                        "column": col,
                        "inferred_type": "string_as_date",
                        "count": row_count,
                        "missing_count": missing,
                        "missing_percentage": missing_pct,
                        "valid_date_count": date_looks,
                        "invalid_date_count": len(str_list[:100]) - date_looks,
                        "min_date": None,
                        "max_date": None,
                        "date_warnings": ["Column stored as text; should be parsed to standard ISO Date."]
                    }

                categorical_profiles[col] = {
                    "column": col,
                    "inferred_type": str(dtype),
                    "count": row_count,
                    "missing_count": missing,
                    "missing_percentage": missing_pct,
                    "unique_count": unique_count,
                    "cardinality_ratio": cardinality_ratio,
                    "top_values": top_values,
                    "is_constant": is_const
                }

        # Calculate overall health score (0 - 100)
        penalty = 0.0
        penalty += min(total_missing_percentage * 0.8, 30.0) # max 30 penalty for nulls
        penalty += min(duplicate_percentage * 1.5, 25.0) # max 25 penalty for duplicates
        for issue in quality_issues:
            if issue["severity"] == "critical":
                penalty += 10.0
            elif issue["severity"] == "warning":
                penalty += 4.0
        health_score = max(0.0, min(100.0, round(100.0 - penalty, 1)))

        return {
            "dataset_id": dataset_id,
            "version_id": version_id,
            "version_number": version_number,
            "row_count": row_count,
            "column_count": col_count,
            "file_size_bytes": file_size_bytes,
            "duplicate_row_count": duplicate_row_count,
            "duplicate_row_percentage": duplicate_percentage,
            "total_missing_values": total_missing,
            "total_missing_percentage": total_missing_percentage,
            "is_sampled": False,
            "sample_size": None,
            "columns": columns,
            "column_types": column_types,
            "numerical_profiles": numerical_profiles,
            "categorical_profiles": categorical_profiles,
            "date_profiles": date_profiles,
            "quality_issues": quality_issues,
            "overall_health_score": health_score
        }
