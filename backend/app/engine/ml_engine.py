from typing import Dict, Any, List, Optional
import polars as pl
import numpy as np

class MLReadinessEngine:
    @classmethod
    def evaluate(
        cls,
        df: pl.DataFrame,
        task_type: str = "classification",
        target_column: Optional[str] = None
    ) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        recommendations: List[Dict[str, Any]] = []
        unresolved_issues: List[str] = []
        rec_step = 1

        total_rows = df.height
        total_cols = df.width
        columns = df.columns
        score = 100.0

        # 1. Target Column Analysis (for supervised tasks)
        if task_type in ("classification", "regression"):
            if not target_column:
                score -= 30.0
                findings.append({
                    "category": "target_quality",
                    "severity": "critical",
                    "issue": "No target column specified",
                    "explanation": f"Supervised task '{task_type}' requires a designated target column.",
                    "rows_affected": total_rows,
                    "sample_values": [],
                    "recommended_operation": "Specify target column"
                })
                unresolved_issues.append("Target column must be designated.")
            elif target_column not in columns:
                score -= 40.0
                findings.append({
                    "category": "target_quality",
                    "severity": "critical",
                    "issue": f"Target column '{target_column}' does not exist",
                    "explanation": f"The selected column '{target_column}' was not found in the dataset schema.",
                    "rows_affected": total_rows,
                    "sample_values": [],
                    "recommended_operation": "Select an existing column as target"
                })
                unresolved_issues.append(f"Target column '{target_column}' missing.")
            else:
                target_series = df[target_column]
                target_nulls = target_series.null_count()
                if target_nulls > 0:
                    score -= 25.0
                    findings.append({
                        "category": "target_quality",
                        "severity": "critical",
                        "issue": f"Target column '{target_column}' contains missing values",
                        "explanation": f"Machine learning models cannot be trained on rows with missing targets ({target_nulls} nulls found).",
                        "rows_affected": target_nulls,
                        "sample_values": [None],
                        "recommended_operation": "drop_missing"
                    })
                    recommendations.append({
                        "step": rec_step,
                        "category": "target_cleaning",
                        "title": f"Drop null target rows in '{target_column}'",
                        "description": f"Filter out {target_nulls} rows with null target values.",
                        "suggested_operation": "drop_missing",
                        "suggested_params": {"columns": [target_column], "how": "any"}
                    })
                    rec_step += 1
                    unresolved_issues.append(f"Target column '{target_column}' has {target_nulls} nulls.")

                # Task-specific checks
                if task_type == "classification":
                    unique_targets = target_series.drop_nulls().unique().len()
                    if unique_targets < 2:
                        score -= 30.0
                        findings.append({
                            "category": "target_quality",
                            "severity": "critical",
                            "issue": "Target has fewer than 2 classes",
                            "explanation": "Classification models require at least two distinct target classes.",
                            "rows_affected": total_rows,
                            "sample_values": target_series.unique().to_list(),
                            "recommended_operation": "verify_target"
                        })
                    elif unique_targets > 100:
                        score -= 20.0
                        findings.append({
                            "category": "target_quality",
                            "severity": "warning",
                            "issue": f"High cardinality target for classification ({unique_targets} classes)",
                            "explanation": "Target has very many classes. If numeric, regression may be more suitable.",
                            "rows_affected": total_rows,
                            "sample_values": target_series.unique()[:5].to_list(),
                            "recommended_operation": "reframe_task"
                        })

                elif task_type == "regression":
                    if not target_series.dtype.is_numeric():
                        score -= 30.0
                        findings.append({
                            "category": "target_quality",
                            "severity": "critical",
                            "issue": f"Non-numeric target '{target_column}' for regression",
                            "explanation": f"Regression models predict continuous numeric values, but '{target_column}' is '{target_series.dtype}'.",
                            "rows_affected": total_rows,
                            "sample_values": target_series.drop_nulls()[:3].to_list(),
                            "recommended_operation": "cast_type"
                        })
                        recommendations.append({
                            "step": rec_step,
                            "category": "type_conversion",
                            "title": f"Cast '{target_column}' to float",
                            "description": "Convert regression target column to numeric float type.",
                            "suggested_operation": "cast_type",
                            "suggested_params": {"column": target_column, "target_type": "float"}
                        })
                        rec_step += 1

        # 2. Feature Columns Analysis
        feature_cols = [c for c in columns if c != target_column]
        has_string_features = False

        for col in feature_cols:
            series = df[col]
            dtype = series.dtype
            null_count = series.null_count()

            # Check missing values
            if null_count > 0:
                pct = round(null_count / total_rows * 100, 1)
                score -= min(pct * 0.15, 8.0)
                findings.append({
                    "category": "missing_data",
                    "severity": "warning" if pct < 30 else "critical",
                    "issue": f"Feature '{col}' contains {null_count} ({pct}%) missing values",
                    "explanation": "Standard ML algorithms (scikit-learn linear models, SVMs, NN) require zero nulls in feature matrices.",
                    "rows_affected": null_count,
                    "sample_values": [None],
                    "recommended_operation": "fill_missing_median" if dtype.is_numeric() else "fill_missing_constant"
                })
                if dtype.is_numeric():
                    recommendations.append({
                        "step": rec_step,
                        "category": "imputation",
                        "title": f"Impute '{col}' with median",
                        "description": f"Fill {null_count} nulls in '{col}' using median value.",
                        "suggested_operation": "fill_missing_median",
                        "suggested_params": {"columns": [col]}
                    })
                else:
                    recommendations.append({
                        "step": rec_step,
                        "category": "imputation",
                        "title": f"Impute '{col}' with 'Unknown'",
                        "description": f"Fill {null_count} nulls in '{col}' using 'Unknown' category.",
                        "suggested_operation": "fill_missing_constant",
                        "suggested_params": {"columns": [col], "value": "Unknown"}
                    })
                rec_step += 1

            # Check constant features
            non_null = series.drop_nulls()
            unique_count = non_null.unique().len()
            if unique_count <= 1:
                score -= 5.0
                findings.append({
                    "category": "feature_types",
                    "severity": "warning",
                    "issue": f"Zero variance feature '{col}'",
                    "explanation": f"Column '{col}' has only {unique_count} distinct value and provides zero predictive information.",
                    "rows_affected": total_rows,
                    "sample_values": non_null[:1].to_list(),
                    "recommended_operation": "drop_column"
                })
                recommendations.append({
                    "step": rec_step,
                    "category": "feature_selection",
                    "title": f"Drop constant column '{col}'",
                    "description": "Remove zero-variance feature to reduce dimensionality.",
                    "suggested_operation": "drop_column",
                    "suggested_params": {"columns": [col]}
                })
                rec_step += 1

            # Check ID column / high cardinality string
            if dtype in (pl.String, pl.Utf8):
                has_string_features = True
                cardinality_ratio = unique_count / total_rows if total_rows > 0 else 0
                if cardinality_ratio > 0.85 and total_rows > 10:
                    score -= 8.0
                    findings.append({
                        "category": "leakage",
                        "severity": "warning",
                        "issue": f"Potential ID / unique identifier column '{col}'",
                        "explanation": f"'{col}' has {unique_count} unique values ({round(cardinality_ratio * 100, 1)}% unique). Including ID keys can cause severe model overfitting.",
                        "rows_affected": total_rows,
                        "sample_values": non_null[:3].to_list(),
                        "recommended_operation": "drop_column"
                    })
                    recommendations.append({
                        "step": rec_step,
                        "category": "leakage_prevention",
                        "title": f"Drop ID column '{col}'",
                        "description": "Exclude high-cardinality identifier from feature inputs.",
                        "suggested_operation": "drop_column",
                        "suggested_params": {"columns": [col]}
                    })
                    rec_step += 1
                elif unique_count <= 20:
                    # Good candidate for one-hot encoding
                    recommendations.append({
                        "step": rec_step,
                        "category": "encoding",
                        "title": f"One-hot encode categorical feature '{col}'",
                        "description": f"Convert {unique_count} categories in '{col}' to binary indicator columns.",
                        "suggested_operation": "one_hot_encode",
                        "suggested_params": {"columns": [col], "drop_first": True}
                    })
                    rec_step += 1

        # 3. Categorical encoding reminder if raw strings exist
        if has_string_features:
            score -= 10.0
            findings.append({
                "category": "feature_types",
                "severity": "warning",
                "issue": "Unencoded string/categorical features present",
                "explanation": "Numerical model algorithms cannot accept raw string columns. One-hot or ordinal encoding is required.",
                "rows_affected": total_rows,
                "sample_values": [],
                "recommended_operation": "one_hot_encode"
            })

        # 4. Train/Test split check
        if "split_assignment" not in columns:
            score -= 5.0
            findings.append({
                "category": "leakage",
                "severity": "info",
                "issue": "No train/test split recorded",
                "explanation": "Preprocessing scalers and encoders should be fit strictly on training splits to prevent data leakage.",
                "rows_affected": total_rows,
                "sample_values": [],
                "recommended_operation": "train_test_split"
            })
            recommendations.append({
                "step": rec_step,
                "category": "data_splitting",
                "title": "Perform train/test split",
                "description": "Split dataset (e.g. 80% train, 20% test) before parameter fitting.",
                "suggested_operation": "train_test_split",
                "suggested_params": {"test_size": 0.2, "random_state": 42}
            })

        final_score = max(0.0, min(100.0, round(score, 1)))
        if final_score >= 80.0 and len(unresolved_issues) == 0:
            overall_status = "ready"
        elif final_score >= 50.0:
            overall_status = "needs_attention"
        else:
            overall_status = "not_ready"

        return {
            "task_type": task_type,
            "target_column": target_column,
            "readiness_score": final_score,
            "overall_status": overall_status,
            "findings": findings,
            "recommendations": recommendations,
            "unresolved_issues": unresolved_issues
        }
