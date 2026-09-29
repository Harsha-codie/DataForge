from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.core.storage import LocalStorageService


client = TestClient(app)


def test_jobs_collection_requires_bearer_token():
    response = client.get("/api/v1/jobs/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication token required."


def test_datasets_collection_requires_bearer_token():
    response = client.get("/api/v1/datasets/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication token required."


def test_visualization_endpoints_require_bearer_token():
    metadata_response = client.get("/api/v1/datasets/dataset/visualizations/metadata")
    chart_response = client.post(
        "/api/v1/datasets/dataset/visualizations/chart",
        json={"chart_type": "histogram", "columns": ["value"]},
    )

    assert metadata_response.status_code == 401
    assert chart_response.status_code == 401


def test_collection_routes_are_registered_with_trailing_slashes():
    routes = set(app.openapi()["paths"])

    assert "/api/v1/jobs/" in routes
    assert "/api/v1/datasets/" in routes


def test_local_storage_rejects_path_traversal(tmp_path):
    storage = LocalStorageService(str(tmp_path / "storage"))

    with pytest.raises(ValueError, match="escapes"):
        storage.exists("../outside.txt")
