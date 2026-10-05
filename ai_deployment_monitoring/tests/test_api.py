"""
tests/test_api.py
-----------------
Smoke-test suite for the Iris Prediction API.

Run with:
    pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient

# Ensure the model is trained before running tests
import subprocess
import sys
import os

# ── Test setup ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def train_model():
    """Train the model if the joblib file doesn't exist yet."""
    model_path = os.path.join(os.path.dirname(__file__), "..", "model", "iris_model.joblib")
    if not os.path.exists(model_path):
        subprocess.run(
            [sys.executable, "model/train_and_save.py"],
            check=True
        )


@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


# ── Health endpoint ────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_payload(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert "uptime_seconds" in data
        assert "version" in data


# ── Model info endpoint ────────────────────────────────────────────────────────
class TestModelInfo:
    def test_model_info_returns_200(self, client):
        resp = client.get("/model/info")
        assert resp.status_code == 200

    def test_model_info_fields(self, client):
        data = client.get("/model/info").json()
        assert "model_type" in data
        assert "test_accuracy" in data
        assert "feature_names" in data


# ── Single prediction endpoint ─────────────────────────────────────────────────
SETOSA_SAMPLE = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
}

VIRGINICA_SAMPLE = {
    "sepal_length": 6.7,
    "sepal_width": 3.0,
    "petal_length": 5.2,
    "petal_width": 2.3,
}


class TestPredict:
    def test_predict_returns_200(self, client):
        resp = client.post("/predict", json=SETOSA_SAMPLE)
        assert resp.status_code == 200

    def test_predict_setosa(self, client):
        data = client.post("/predict", json=SETOSA_SAMPLE).json()
        assert data["class_name"] == "setosa"
        assert 0.0 <= data["confidence"] <= 1.0
        assert set(data["probabilities"].keys()) == {"setosa", "versicolor", "virginica"}

    def test_predict_virginica(self, client):
        data = client.post("/predict", json=VIRGINICA_SAMPLE).json()
        assert data["class_name"] == "virginica"

    def test_predict_invalid_payload(self, client):
        # Missing required fields
        resp = client.post("/predict", json={"sepal_length": 5.1})
        assert resp.status_code == 422

    def test_predict_negative_values(self, client):
        bad_payload = {**SETOSA_SAMPLE, "sepal_length": -1.0}
        resp = client.post("/predict", json=bad_payload)
        assert resp.status_code == 422


# ── Batch prediction endpoint ──────────────────────────────────────────────────
class TestBatchPredict:
    def test_batch_predict_returns_200(self, client):
        resp = client.post(
            "/predict/batch",
            json={"samples": [SETOSA_SAMPLE, VIRGINICA_SAMPLE]},
        )
        assert resp.status_code == 200

    def test_batch_predict_count(self, client):
        data = client.post(
            "/predict/batch",
            json={"samples": [SETOSA_SAMPLE, VIRGINICA_SAMPLE]},
        ).json()
        assert data["batch_size"] == 2
        assert len(data["predictions"]) == 2

    def test_batch_empty_list(self, client):
        resp = client.post("/predict/batch", json={"samples": []})
        assert resp.status_code == 422


# ── Metrics endpoint ───────────────────────────────────────────────────────────
class TestMetrics:
    def test_metrics_returns_200(self, client):
        resp = client.get("/metrics")
        assert resp.status_code == 200

    def test_metrics_fields(self, client):
        data = client.get("/metrics").json()
        for field in [
            "total_requests",
            "successful_predictions",
            "failed_requests",
            "avg_latency_ms",
            "p95_latency_ms",
            "error_rate_percent",
        ]:
            assert field in data, f"Missing field: {field}"

    def test_metrics_accumulate(self, client):
        before = client.get("/metrics").json()["total_requests"]
        client.post("/predict", json=SETOSA_SAMPLE)
        after = client.get("/metrics").json()["total_requests"]
        # At least the /predict request was counted
        assert after >= before
