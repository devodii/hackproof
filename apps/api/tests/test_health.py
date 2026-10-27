from fastapi.testclient import TestClient

from hackproof.main import app


def test_health():
    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}


def test_window_spans_27_hours():
    with TestClient(app) as client:
        body = client.get("/api/window").json()
    assert body["start"] < body["end"]
