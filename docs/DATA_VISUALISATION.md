# Data Visualisation

DataForge provides an authenticated, dataset-version-aware EDA workspace at:

`/datasets/{dataset_id}/visualizations`

The page uses the active version selected in the dataset workspace. Chart data is computed by the backend from the canonical Parquet version, so the browser does not receive the entire dataset.

## Supported charts

- Histogram with configurable bins
- KDE density plot
- Box plot and IQR outlier analysis
- Categorical bar chart and class distribution
- Violin density plot
- Numerical scatter plot with correlation insight
- Pearson and Spearman correlation heatmaps
- Pair plot data for up to four numerical columns
- Ordered/date line chart
- Grouped box plot
- Missing-value bar chart and sampled missing-value heatmap

The page also displays rule-based recommendations based on detected numerical, categorical, date, and missing-value columns.

## API

All endpoints use the existing `/api/v1` prefix and Bearer authentication.

### Metadata

`GET /api/v1/datasets/{dataset_id}/visualizations/metadata?version_id={version_id}`

The response includes dataset/version metadata, inferred numeric/categorical/date columns, columns containing missing values, and recommended chart requests.

### Generate a chart

`POST /api/v1/datasets/{dataset_id}/visualizations/chart?version_id={version_id}`

Example body:

```json
{
  "chart_type": "histogram",
  "columns": ["age"],
  "bins": 20,
  "correlation_method": "pearson",
  "sample_size": 5000
}
```

The response includes `chart_type`, `title`, bounded `data`, statistical `insights`, and metadata describing sampling and selected columns.

## Limits and behavior

- Requests validate column names and chart-specific column types.
- Chart payloads are bounded. Row-level charts sample up to 5,000 rows by default; pair plots support up to four columns; categorical frequencies are limited to the top 30 values/groups.
- Missing heatmaps sample up to 200 rows to keep the response readable.
- Empty or constant numerical columns return empty/limited statistics rather than fabricated values.
- Machine-learning evaluation plots are not included because DataForge does not currently have a model-training/evaluation workflow.
- The browser PNG action exports the rendered SVG chart where the browser supports canvas export.
