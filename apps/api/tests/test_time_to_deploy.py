from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from hackproof.main import app
from hackproof.queries import compute_deploy_histogram


@pytest.fixture(autouse=True)
def mock_pool_lifespan(monkeypatch):
    monkeypatch.setattr("hackproof.main.open_pool", AsyncMock())
    monkeypatch.setattr("hackproof.main.close_pool", AsyncMock())


def test_bucketing_function_with_three_projects_fixture():
    # Acceptance criteria: A fixture with three projects produces the expected buckets and median
    deltas = [15.0, 45.0, 75.0]
    buckets, median = compute_deploy_histogram(deltas, bucket_size=30)

    assert median == 45.0
    assert len(buckets) == 3

    assert buckets[0]["label"] == "0-30m"
    assert buckets[0]["count"] == 1
    assert buckets[0]["min_minutes"] == 0
    assert buckets[0]["max_minutes"] == 30

    assert buckets[1]["label"] == "30-60m"
    assert buckets[1]["count"] == 1
    assert buckets[1]["min_minutes"] == 30
    assert buckets[1]["max_minutes"] == 60

    assert buckets[2]["label"] == "60-90m"
    assert buckets[2]["count"] == 1
    assert buckets[2]["min_minutes"] == 60
    assert buckets[2]["max_minutes"] == 90


def test_bucketing_function_edge_cases():
    # 1. Empty input
    buckets, median = compute_deploy_histogram([])
    assert buckets == []
    assert median is None

    # 2. Clustered in same bucket
    buckets, median = compute_deploy_histogram([5.0, 10.0, 20.0], bucket_size=30)
    assert median == 10.0
    assert len(buckets) == 1
    assert buckets[0]["count"] == 3

    # 3. Even count calculates midpoint median
    buckets, median = compute_deploy_histogram([10.0, 20.0, 30.0, 40.0], bucket_size=30)
    assert median == 25.0

    # 4. Negative values clamped to 0
    buckets, median = compute_deploy_histogram([-10.0, 25.0], bucket_size=30)
    assert median == 12.5
    assert buckets[0]["count"] == 2


def test_time_to_deploy_api_endpoint(monkeypatch):
    mock_payload = {
        "total_projects": 3,
        "median_minutes": 45.0,
        "buckets": [
            {"bucket_index": 0, "min_minutes": 0, "max_minutes": 30, "label": "0-30m", "count": 1},
            {
                "bucket_index": 1,
                "min_minutes": 30,
                "max_minutes": 60,
                "label": "30-60m",
                "count": 1,
            },
            {
                "bucket_index": 2,
                "min_minutes": 60,
                "max_minutes": 90,
                "label": "60-90m",
                "count": 1,
            },
        ],
    }

    monkeypatch.setattr(
        "hackproof.queries.fetch_time_to_deploy", AsyncMock(return_value=mock_payload)
    )

    with TestClient(app) as client:
        resp = client.get("/api/time-to-deploy")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_projects"] == 3
        assert data["median_minutes"] == 45.0
        assert len(data["buckets"]) == 3
        assert data["buckets"][0]["label"] == "0-30m"
        assert data["buckets"][0]["count"] == 1
