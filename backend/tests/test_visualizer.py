import polars as pl
import pytest

from app.engine.visualizer import generate_chart, metadata


@pytest.fixture
def sample_frame():
    return pl.DataFrame(
        {
            "age": [20, 21, 22, 23, None, 100],
            "income": [30.0, 31.0, 33.0, 35.0, 36.0, 90.0],
            "segment": ["A", "A", "B", "B", "B", "A"],
        }
    )


def test_metadata_recommends_charts_and_classifies_columns(sample_frame):
    result = metadata(sample_frame, "dataset", "version", 1)

    assert result["numeric_columns"] == ["age", "income"]
    assert result["categorical_columns"] == ["segment"]
    assert "age" in result["missing_columns"]
    assert any(item["chart_type"] == "scatter" for item in result["recommendations"])


def test_histogram_is_bounded_and_reports_insights(sample_frame):
    result = generate_chart(sample_frame, "histogram", ["age"], None, None, None, 5, "pearson", 100)

    assert len(result["data"]) == 5
    assert result["insights"][0]["label"] == "Mean"
    assert result["metadata"]["sample_size"] == 6


def test_missing_values_and_grouped_box(sample_frame):
    missing = generate_chart(sample_frame, "missing_bar", [], None, None, None, 20, "pearson", 100)
    grouped = generate_chart(sample_frame, "grouped_box", ["income", "segment"], None, None, None, 20, "pearson", 100)

    assert missing["data"][0]["missing"] == 1
    assert {item["group"] for item in grouped["data"]} == {"A", "B"}


def test_invalid_column_and_chart_type_are_rejected(sample_frame):
    with pytest.raises(ValueError, match="Unknown column"):
        generate_chart(sample_frame, "histogram", ["unknown"], None, None, None, 20, "pearson", 100)

    with pytest.raises(ValueError, match="numerical column"):
        generate_chart(sample_frame, "histogram", ["segment"], None, None, None, 20, "pearson", 100)
