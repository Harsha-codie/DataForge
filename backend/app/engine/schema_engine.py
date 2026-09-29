import re
from typing import Dict, Any, List, Optional
import polars as pl
from datetime import datetime, timezone

class SchemaEngine:
    TYPE_MAPPINGS = {
        "integer": [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64],
        "float": [pl.Float32, pl.Float64, pl.Decimal],
        "string": [pl.String, pl.Utf8],
        "categorical": [pl.Categorical, pl.String, pl.Utf8],
        "boolean": [pl.Boolean],
        "date": [pl.Date],
        "datetime": [pl.Datetime],
    }

    @classmethod
    def is_type_compatible(cls, polars_dtype: pl.DataType, expected_type_str: str) -> bool:
        expected = expected_type_str.lower().strip()
        matching_types = cls.TYPE_MAPPINGS.get(expected, [])
        if polars_dtype in matching_types:
            return True
        # Numeric generalization: integers are compatible with float expected type
        if expected == "float" and polars_dtype.is_numeric():
            return True
        return False

    @classmethod
    def compare_schema(
        cls,
        df: pl.DataFrame,
        expected_columns: List[Dict[str, Any]],
        dataset_id: str,
        version_id: str,
        schema_id: Optional[str] = None
    ) -> Dict[str, Any]:
        actual_cols = df.columns
        actual_types = {col: str(dtype) for col, dtype in zip(actual_cols, df.dtypes)}
        expected_names = [c["name"] for c in expected_columns]
        expected_map = {c["name"]: c for c in expected_columns}

        missing_columns = [name for name in expected_names if name not in actual_cols]
        unexpected_columns = [col for col in actual_cols if col not in expected_map]

        issues: List[Dict[str, Any]] = []
        column_details: List[Dict[str, Any]] = []
        matched_count = 0

        # 1. Missing columns
        for miss in missing_columns:
            cfg = expected_map[miss]
            is_req = cfg.get("required", True)
            issues.append({
                "column": miss,
                "severity": "critical" if is_req else "warning",
                "issue_type": "missing_column",
                "message": f"Required column '{miss}' is missing from the dataset." if is_req else f"Optional column '{miss}' is missing.",
                "expected_type": cfg.get("data_type"),
                "actual_type": None,
                "affected_rows": df.height,
                "sample_values": [],
                "suggested_action": "Check dataset source or add column with default values."
            })

        # 2. Analyze existing columns
        for col_name in actual_cols:
            series = df[col_name]
            dtype = series.dtype
            exp_cfg = expected_map.get(col_name)

            if not exp_cfg:
                # Unexpected column
                column_details.append({
                    "name": col_name,
                    "status": "unexpected",
                    "expected_type": None,
                    "actual_type": str(dtype),
                    "incompatible_count": 0,
                    "null_violations": 0,
                    "sample_invalid_values": []
                })
                continue

            matched_count += 1
            exp_type = exp_cfg.get("data_type", "string").lower().strip()
            nullable = exp_cfg.get("nullable", True)
            allowed_values = exp_cfg.get("allowed_values")
            min_val = exp_cfg.get("min_value")
            max_val = exp_cfg.get("max_value")
            regex_pat = exp_cfg.get("regex_pattern")

            col_issues = []
            null_count = series.null_count()
            null_violations = 0

            # Check nullability
            if not nullable and null_count > 0:
                null_violations = null_count
                issues.append({
                    "column": col_name,
                    "severity": "critical",
                    "issue_type": "nullability_violation",
                    "message": f"Column '{col_name}' contains {null_count} null values but is marked non-nullable.",
                    "expected_type": exp_type,
                    "actual_type": str(dtype),
                    "affected_rows": null_count,
                    "sample_values": [None],
                    "suggested_action": "Fill missing values or drop null rows."
                })

            # Check data type compatibility
            type_compat = cls.is_type_compatible(dtype, exp_type)
            incompatible_rows = 0
            sample_invalids: List[Any] = []

            if not type_compat:
                # E.g. String column expecting integer or float
                # Let's inspect the actual values to detect mixed-type or convertible values
                non_nulls = series.drop_nulls()
                incompatible_samples = []

                if exp_type in ("integer", "float"):
                    for val in non_nulls.to_list()[:500]:
                        s_val = str(val).replace("$", "").replace(",", "").strip()
                        try:
                            if exp_type == "integer":
                                int(s_val)
                            else:
                                float(s_val)
                        except (ValueError, TypeError):
                            incompatible_rows += 1
                            if len(incompatible_samples) < 5:
                                incompatible_samples.append(val)

                    # Scale estimate if sampled
                    if non_nulls.len() > 500:
                        incompatible_rows = int((incompatible_rows / 500) * non_nulls.len())

                    issues.append({
                        "column": col_name,
                        "severity": "critical",
                        "issue_type": "type_mismatch",
                        "message": f"Column '{col_name}' is '{dtype}' but expected '{exp_type}'. {incompatible_rows} values cannot be parsed cleanly.",
                        "expected_type": exp_type,
                        "actual_type": str(dtype),
                        "affected_rows": incompatible_rows,
                        "sample_values": incompatible_samples,
                        "suggested_action": f"Cast column '{col_name}' to {exp_type} with invalid value handling."
                    })
                    sample_invalids.extend(incompatible_samples)

                elif exp_type == "date":
                    issues.append({
                        "column": col_name,
                        "severity": "warning",
                        "issue_type": "type_mismatch",
                        "message": f"Column '{col_name}' is stored as '{dtype}' rather than Date/Datetime.",
                        "expected_type": "date",
                        "actual_type": str(dtype),
                        "affected_rows": df.height,
                        "sample_values": [str(x) for x in non_nulls.to_list()[:3]],
                        "suggested_action": "Apply date parsing transformation."
                    })
            else:
                # Type matches, check specific value constraints
                non_nulls = series.drop_nulls()

                # Check allowed values (enum)
                if allowed_values is not None and len(allowed_values) > 0:
                    allowed_set = set(str(v).lower() for v in allowed_values)
                    violators = []
                    violator_count = 0
                    for val in non_nulls.to_list():
                        if str(val).lower() not in allowed_set:
                            violator_count += 1
                            if len(violators) < 5:
                                violators.append(val)
                    if violator_count > 0:
                        issues.append({
                            "column": col_name,
                            "severity": "warning",
                            "issue_type": "enum_violation",
                            "message": f"Found {violator_count} values outside allowed set {allowed_values}.",
                            "expected_type": exp_type,
                            "actual_type": str(dtype),
                            "affected_rows": violator_count,
                            "sample_values": violators,
                            "suggested_action": "Normalize or filter unexpected category values."
                        })
                        sample_invalids.extend(violators)

                # Check numeric min/max constraints
                if dtype.is_numeric() and (min_val is not None or max_val is not None):
                    num_arr = non_nulls.to_numpy()
                    range_violators = []
                    violator_count = 0
                    for v in num_arr:
                        if (min_val is not None and v < min_val) or (max_val is not None and v > max_val):
                            violator_count += 1
                            if len(range_violators) < 5:
                                range_violators.append(float(v))
                    if violator_count > 0:
                        issues.append({
                            "column": col_name,
                            "severity": "warning",
                            "issue_type": "constraint_violation",
                            "message": f"Found {violator_count} numeric values violating bounds [{min_val}, {max_val}].",
                            "expected_type": exp_type,
                            "actual_type": str(dtype),
                            "affected_rows": violator_count,
                            "sample_values": range_violators,
                            "suggested_action": f"Clip or filter values outside range [{min_val}, {max_val}]."
                        })
                        sample_invalids.extend(range_violators)

                # Check regex pattern
                if regex_pat and (dtype == pl.String or dtype == pl.Utf8):
                    try:
                        pattern = re.compile(regex_pat)
                        violators = []
                        violator_count = 0
                        for v in non_nulls.to_list()[:500]:
                            if not pattern.match(str(v)):
                                violator_count += 1
                                if len(violators) < 5:
                                    violators.append(v)
                        if violator_count > 0:
                            issues.append({
                                "column": col_name,
                                "severity": "warning",
                                "issue_type": "constraint_violation",
                                "message": f"Column '{col_name}' has values failing regex '{regex_pat}'.",
                                "expected_type": exp_type,
                                "actual_type": str(dtype),
                                "affected_rows": violator_count,
                                "sample_values": violators,
                                "suggested_action": "Normalize text or remove non-conforming records."
                            })
                            sample_invalids.extend(violators)
                    except re.error:
                        pass

            col_status = "matched"
            if not type_compat or incompatible_rows > 0:
                col_status = "type_mismatch"
            elif null_violations > 0 or len(sample_invalids) > 0:
                col_status = "constraint_violation"

            column_details.append({
                "name": col_name,
                "status": col_status,
                "expected_type": exp_type,
                "actual_type": str(dtype),
                "incompatible_count": incompatible_rows,
                "null_violations": null_violations,
                "sample_invalid_values": sample_invalids[:5]
            })

        # Determine overall compatibility status
        has_critical = any(issue["severity"] == "critical" for issue in issues)
        has_warning = any(issue["severity"] == "warning" for issue in issues)

        if has_critical:
            overall_status = "incompatible"
        elif has_warning:
            overall_status = "warnings"
        else:
            overall_status = "compatible"

        return {
            "dataset_id": dataset_id,
            "version_id": version_id,
            "schema_id": schema_id,
            "compatibility_status": overall_status,
            "total_expected_columns": len(expected_columns),
            "matched_columns_count": matched_count,
            "missing_columns": missing_columns,
            "unexpected_columns": unexpected_columns,
            "issues": issues,
            "column_details": column_details,
            "created_at": datetime.now(timezone.utc)
        }
