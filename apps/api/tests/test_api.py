from fastapi.testclient import TestClient

from hackproof.main import app


def test_stats_reports_every_counter():
    with TestClient(app) as client:
        body = client.get("/api/stats").json()
    assert set(body) == {
        "projects",
        "verified_projects",
        "likely_projects",
        "possible_projects",
        "unattributed_accounts",
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


def test_projects_can_be_filtered_by_tier():
    with TestClient(app) as client:
        body = client.get("/api/projects", params={"tier": ["verified", "likely"], "limit": 100})
    assert {item["tier"] for item in body.json()["items"]} <= {"verified", "likely"}


def test_timeline_has_one_point_per_hour_of_the_window():
    with TestClient(app) as client:
        points = client.get("/api/timeline").json()
    assert len(points) == 27
    assert all(point["contracts"] >= 0 for point in points)


def test_countries_are_ranked_by_contributors():
    with TestClient(app) as client:
        rows = client.get("/api/countries").json()
    counts = [row["contributors"] for row in rows]
    assert counts == sorted(counts, reverse=True)


def test_integrations_list_every_partner_with_a_project_count():
    with TestClient(app) as client:
        body = client.get("/api/integrations").json()
    assert {"trustless-work", "privy", "stellar-wallets-kit"} <= {row["slug"] for row in body}
    assert all(row["projects"] >= 0 for row in body)


def test_projects_can_be_filtered_by_integration_partner():
    with TestClient(app) as client:
        none = client.get("/api/projects", params={"integration": "no-such-partner"}).json()
        assert none["total"] == 0
        used = next(
            (row for row in client.get("/api/integrations").json() if row["projects"]), None
        )
        if used:
            body = client.get("/api/projects", params={"integration": used["slug"]}).json()
            assert body["total"] >= used["projects"]
            assert all(used["slug"] in item["integrations"] for item in body["items"])
