"""Integration tests for FastAPI endpoints."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

SAMPLE_ROW = {
    "ret_mean_10s": 0.000001,
    "ret_std_10s": 0.000012,
    "ret_abs_10s": 0.000008,
    "tick_count_10s": 25,
    "spread_mean_10s": 0.000002,
    "trade_intensity_10s": 2.5,
    "ret_mean_30s": 0.000001,
    "ret_std_30s": 0.000015,
    "ret_abs_30s": 0.000010,
    "tick_count_30s": 35,
    "spread_mean_30s": 0.000002,
    "trade_intensity_30s": 3.0,
    "ret_mean_60s": 0.000001,
    "ret_std_60s": 0.000020,
    "ret_abs_60s": 0.000012,
    "tick_count_60s": 45,
    "spread_mean_60s": 0.000002,
    "trade_intensity_60s": 3.5,
    "spread_bps": 0.05,
    "mid_price": 66900.0,
}

SAMPLE_FEATURES = {**SAMPLE_ROW, "product_id": "BTC-USD"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert "version" in data
    assert "features" in data


def test_metrics_prometheus():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_request" in response.text


def test_metrics_json():
    response = client.get("/metrics/json")
    assert response.status_code == 200
    data = response.json()
    assert "total_predictions" in data
    assert "status" in data


def test_predict_rows():
    """Test the rows-based /predict endpoint."""
    response = client.post("/predict", json={"rows": [SAMPLE_ROW]})
    assert response.status_code == 200
    data = response.json()
    assert "scores" in data
    assert len(data["scores"]) == 1
    assert 0.0 <= data["scores"][0] <= 1.0
    assert data["model_variant"] == "ml"
    assert "version" in data
    assert "ts" in data


def test_predict_rows_batch():
    """Test batch prediction with multiple rows."""
    response = client.post("/predict", json={"rows": [SAMPLE_ROW, SAMPLE_ROW]})
    assert response.status_code == 200
    data = response.json()
    assert len(data["scores"]) == 2


def test_predict_legacy():
    """Test the legacy single-row /predict/legacy endpoint."""
    response = client.post("/predict/legacy", json={"features": SAMPLE_FEATURES})
    assert response.status_code == 200
    data = response.json()
    assert "spike_probability" in data
    assert "spike_predicted" in data
    assert 0.0 <= data["spike_probability"] <= 1.0


def test_predict_legacy_returns_product_id():
    response = client.post("/predict/legacy", json={"features": SAMPLE_FEATURES})
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "BTC-USD"
