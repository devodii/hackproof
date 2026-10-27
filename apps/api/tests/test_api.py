from fastapi.testclient import TestClient

from hackproof.main import app


def test_stats_reports_every_counter():
    with TestClient(app) as client:
        body = client.get("/api/stats").json()
    assert set(body) == {
        "projects",
        "contract_projects",
        "classic_projects",
        "github_projects",
        "linked_projects",
        "contracts",
        "builders",
        "contributors",
        "countries",
        "wasm_uploads",
        "failed_txs",
    }


def test_lists_are_paginated():
    with TestClient(app) as client:
        for path in ("projects", "contracts", "wasm", "failed"):
            body = client.get(f"/api/{path}", params={"limit": 3}).json()
            assert len(body["items"]) <= 3
            assert body["total"] >= len(body["items"])


def test_limit_is_bounded():
    with TestClient(app) as client:
        assert client.get("/api/projects", params={"limit": 5000}).status_code == 422


def test_unknown_project_and_builder_are_not_found():
    with TestClient(app) as client:
        assert client.get("/api/projects/repo:nobody/nothing").status_code == 404
        assert client.get("/api/builders/GNOBODY").status_code == 404
