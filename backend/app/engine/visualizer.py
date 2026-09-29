from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import polars as pl


NUMERIC_TYPES = {
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64,
}


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _numeric_columns(df: pl.DataFrame) -> List[str]:
    return [name for name, dtype in zip(df.columns, df.dtypes) if dtype in NUMERIC_TYPES]


def _date_columns(df: pl.DataFrame) -> List[str]:
    return [name for name, dtype in zip(df.columns, df.dtypes) if dtype in (pl.Date, pl.Datetime)]


def _categorical_columns(df: pl.DataFrame) -> List[str]:
    numeric = set(_numeric_columns(df))
    dates = set(_date_columns(df))
    return [name for name in df.columns if name not in numeric and name not in dates]


def _column_type(dtype: pl.DataType) -> str:
    if dtype in NUMERIC_TYPES:
        return "numeric"
    if dtype in (pl.Date, pl.Datetime):
        return "date"
    return "categorical"


def _require_columns(df: pl.DataFrame, columns: Iterable[Optional[str]]) -> List[str]:
    selected = [column for column in columns if column]
    missing = [column for column in selected if column not in df.columns]
    if missing:
        raise ValueError(f"Unknown column(s): {', '.join(missing)}")
    return selected


def _numeric_values(df: pl.DataFrame, column: str) -> np.ndarray:
    values = df.get_column(column).drop_nulls().to_numpy()
    values = np.asarray(values, dtype=float)
    return values[np.isfinite(values)]


def _sample_frame(df: pl.DataFrame, sample_size: int) -> pl.DataFrame:
    if df.height <= sample_size:
        return df
    return df.sample(n=sample_size, with_replacement=False, seed=42)


def _recommendations(df: pl.DataFrame) -> List[Dict[str, Any]]:
    numeric = _numeric_columns(df)
    categorical = _categorical_columns(df)
    recommendations: List[Dict[str, Any]] = []
    if numeric:
        recommendations.extend([
            {"chart_type": "histogram", "columns": [numeric[0]], "reason": "Inspect the frequency distribution."},
            {"chart_type": "kde", "columns": [numeric[0]], "reason": "Inspect the smoothed distribution shape."},
            {"chart_type": "box", "columns": [numeric[0]], "reason": "Review spread and potential outliers."},
        ])
    if categorical:
        recommendations.append({"chart_type": "bar", "columns": [categorical[0]], "reason": "Compare category frequencies."})
    if len(numeric) >= 2:
        recommendations.extend([
            {"chart_type": "scatter", "columns": numeric[:2], "reason": "Compare two numerical features."},
            {"chart_type": "correlation_heatmap", "columns": numeric[:6], "reason": "Review linear relationships between numerical features."},
        ])
    if numeric and categorical:
        recommendations.append({"chart_type": "grouped_box", "columns": [numeric[0], categorical[0]], "reason": "Compare numerical spread across groups."})
    missing = [column for column in df.columns if df.get_column(column).null_count() > 0]
    if missing:
        recommendations.extend([
            {"chart_type": "missing_bar", "columns": [], "reason": "Quantify missing values by column."},
            {"chart_type": "missing_heatmap", "columns": [], "reason": "Find row-level missingness patterns."},
        ])
    return recommendations


def metadata(df: pl.DataFrame, dataset_id: str, version_id: str, version_number: int) -> Dict[str, Any]:
    numeric = _numeric_columns(df)
    categorical = _categorical_columns(df)
    dates = _date_columns(df)
    return {
        "dataset_id": dataset_id,
        "version_id": version_id,
        "version_number": version_number,
        "row_count": df.height,
        "columns": df.columns,
        "column_types": {name: _column_type(dtype) for name, dtype in zip(df.columns, df.dtypes)},
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "date_columns": dates,
        "missing_columns": [name for name in df.columns if df.get_column(name).null_count() > 0],
        "recommendations": _recommendations(df),
    }


def _distribution_stats(values: np.ndarray) -> Dict[str, Any]:
    if len(values) == 0:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": int(len(values)),
        "mean": round(float(np.mean(values)), 4),
        "median": round(float(np.median(values)), 4),
        "min": round(float(np.min(values)), 4),
        "max": round(float(np.max(values)), 4),
    }


def _histogram(values: np.ndarray, bins: int) -> List[Dict[str, Any]]:
    if len(values) == 0:
        return []
    if np.min(values) == np.max(values):
        return [{"bin_start": float(values[0]), "bin_end": float(values[0]), "count": int(len(values))}]
    counts, edges = np.histogram(values, bins=bins)
    return [{"bin_start": round(float(edges[i]), 6), "bin_end": round(float(edges[i + 1]), 6), "count": int(counts[i])} for i in range(len(counts))]


def _kde(values: np.ndarray) -> List[Dict[str, float]]:
    if len(values) < 2 or np.min(values) == np.max(values):
        return []
    bandwidth = max(1.06 * np.std(values) * len(values) ** (-1 / 5), 1e-9)
    x_values = np.linspace(float(np.min(values)), float(np.max(values)), 80)
    density = np.exp(-0.5 * ((x_values[:, None] - values[None, :]) / bandwidth) ** 2).sum(axis=1)
    density /= len(values) * bandwidth * math.sqrt(2 * math.pi)
    return [{"x": round(float(x), 6), "density": round(float(y), 8)} for x, y in zip(x_values, density)]


def _box(values: np.ndarray) -> Dict[str, Any]:
    if len(values) == 0:
        return {"count": 0, "min": None, "q1": None, "median": None, "q3": None, "max": None, "outlier_count": 0, "outliers": []}
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = values[(values < low) | (values > high)]
    return {"count": int(len(values)), "min": float(np.min(values)), "q1": float(q1), "median": float(median), "q3": float(q3), "max": float(np.max(values)), "lower_fence": float(low), "upper_fence": float(high), "outlier_count": int(len(outliers)), "outliers": [float(value) for value in outliers[:100]]}


def generate_chart(df: pl.DataFrame, chart_type: str, columns: List[str], x_column: Optional[str], y_column: Optional[str], group_column: Optional[str], bins: int, correlation_method: str, sample_size: int) -> Dict[str, Any]:
    selected = _require_columns(df, [*columns, x_column, y_column, group_column])
    numeric = set(_numeric_columns(df))
    categorical = set(_categorical_columns(df))
    frame = _sample_frame(df, sample_size)
    title = chart_type.replace("_", " ").title()
    insights: List[Dict[str, Any]] = []

    if chart_type in {"histogram", "kde", "box", "violin", "outlier"}:
        column = selected[0] if selected else None
        if not column or column not in numeric:
            raise ValueError("This chart requires one numerical column")
        values = _numeric_values(frame, column)
        stats = _distribution_stats(values)
        if chart_type == "histogram":
            data = _histogram(values, bins)
            insights = [{"label": "Mean", "value": stats["mean"]}, {"label": "Median", "value": stats["median"]}]
        elif chart_type == "kde":
            data = _kde(values)
            insights = [{"label": "Observations", "value": stats["count"]}, {"label": "Mean", "value": stats["mean"]}]
        elif chart_type == "violin":
            data = _kde(values)
            insights = [{"label": "Observations", "value": stats["count"]}, {"label": "Median", "value": stats["median"]}]
        else:
            data = [{"column": column, **_box(values)}]
            box = data[0]
            insights = [{"label": "Median", "value": box["median"]}, {"label": "Potential outliers", "value": box["outlier_count"]}]
        return {"chart_type": chart_type, "title": f"{title}: {column}", "data": data, "insights": insights, "metadata": {"sampled": frame.height < df.height, "sample_size": frame.height, "row_count": df.height, "column": column}}

    if chart_type == "bar" or chart_type == "class_distribution":
        column = selected[0] if selected else None
        if not column or column not in categorical:
            raise ValueError("This chart requires one categorical column")
        grouped = frame.group_by(column, maintain_order=False).len(name="count").sort("count", descending=True).head(30)
        total = frame.height or 1
        data = [{"value": str(row[column]), "count": int(row["count"]), "percentage": round(int(row["count"]) / total * 100, 2)} for row in grouped.to_dicts()]
        insights = [{"label": "Categories shown", "value": len(data)}, {"label": "Largest class", "value": data[0]["value"] if data else None}]
        return {"chart_type": chart_type, "title": f"{title}: {column}", "data": data, "insights": insights, "metadata": {"sampled": frame.height < df.height, "sample_size": frame.height, "row_count": df.height, "column": column}}

    if chart_type == "scatter":
        if len(selected) < 2 or selected[0] not in numeric or selected[1] not in numeric:
            raise ValueError("Scatter plot requires two numerical columns")
        pairs = frame.select(selected[:2]).drop_nulls().to_dicts()
        data = [{"x": _json_value(row[selected[0]]), "y": _json_value(row[selected[1]])} for row in pairs]
        corr = float(np.corrcoef([point["x"] for point in data], [point["y"] for point in data])[0, 1]) if len(data) > 1 else None
        insights = [{"label": "Correlation", "value": round(corr, 4) if corr is not None and math.isfinite(corr) else None}]
        return {"chart_type": chart_type, "title": f"{selected[0]} vs {selected[1]}", "data": data, "insights": insights, "metadata": {"sampled": frame.height < df.height, "sample_size": len(data), "row_count": df.height, "x_column": selected[0], "y_column": selected[1]}}

    if chart_type == "correlation_heatmap":
        chosen = [column for column in selected if column in numeric][:6]
        if len(chosen) < 2:
            raise ValueError("Correlation heatmap requires at least two numerical columns")
        matrix = frame.select(chosen).to_pandas().corr(method=correlation_method)
        data = [{"x": x, "y": y, "value": round(float(matrix.loc[y, x]), 5) if not math.isnan(matrix.loc[y, x]) else None} for y in chosen for x in chosen]
        return {"chart_type": chart_type, "title": f"{correlation_method.title()} correlation", "data": data, "insights": [{"label": "Features", "value": len(chosen)}, {"label": "Method", "value": correlation_method}], "metadata": {"columns": chosen, "row_count": df.height}}

    if chart_type == "pair_plot":
        chosen = [column for column in selected if column in numeric][:4]
        if len(chosen) < 2:
            raise ValueError("Pair plot requires at least two numerical columns")
        data = [{column: _json_value(row[column]) for column in chosen} for row in frame.select(chosen).drop_nulls().to_dicts()]
        return {"chart_type": chart_type, "title": "Pair plot", "data": data, "insights": [{"label": "Features", "value": len(chosen)}], "metadata": {"columns": chosen, "sampled": frame.height < df.height, "sample_size": len(data), "row_count": df.height}}

    if chart_type == "grouped_box":
        if len(selected) < 2 or selected[0] not in numeric or selected[1] not in categorical:
            raise ValueError("Grouped box plot requires a numerical and categorical column")
        groups = frame.select([selected[0], selected[1]]).drop_nulls().group_by(selected[1], maintain_order=False)
        data = []
        for group_key, group_frame in groups:
            group = group_key[0] if isinstance(group_key, tuple) else group_key
            data.append({"group": str(group), **_box(_numeric_values(group_frame, selected[0]))})
        return {"chart_type": chart_type, "title": f"{selected[0]} by {selected[1]}", "data": data[:30], "insights": [{"label": "Groups shown", "value": len(data[:30])}], "metadata": {"row_count": df.height}}

    if chart_type == "line":
        if len(selected) < 2 or selected[1] not in numeric or (selected[0] not in numeric and selected[0] not in set(_date_columns(df))):
            raise ValueError("Line chart requires an ordered/date column and a numerical column")
        data = [{"x": str(row[selected[0]]), "y": _json_value(row[selected[1]])} for row in frame.select(selected[:2]).drop_nulls().sort(selected[0]).head(2000).to_dicts()]
        return {"chart_type": chart_type, "title": f"{selected[1]} over {selected[0]}", "data": data, "insights": [{"label": "Points shown", "value": len(data)}], "metadata": {"row_count": df.height}}

    if chart_type == "missing_bar":
        data = [{"column": column, "missing": int(df.get_column(column).null_count()), "percentage": round(df.get_column(column).null_count() / (df.height or 1) * 100, 2)} for column in df.columns]
        return {"chart_type": chart_type, "title": "Missing values by column", "data": data, "insights": [{"label": "Columns with missing values", "value": sum(1 for item in data if item["missing"] > 0)}], "metadata": {"row_count": df.height}}

    if chart_type == "missing_heatmap":
        heat_frame = _sample_frame(df, min(sample_size, 200)).select(df.columns)
        data = [{"row": index, "column": column, "missing": heat_frame.get_column(column)[index] is None} for index in range(heat_frame.height) for column in df.columns]
        return {"chart_type": chart_type, "title": "Missing value pattern", "data": data, "insights": [{"label": "Rows shown", "value": heat_frame.height}], "metadata": {"row_count": df.height, "sampled": heat_frame.height < df.height}}

    raise ValueError(f"Unsupported chart type: {chart_type}")
