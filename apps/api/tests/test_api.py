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


def test_a_project_page_lists_where_each_integration_was_found():
    with TestClient(app) as client:
        used = next(
            (row for row in client.get("/api/integrations").json() if row["projects"]), None
        )
        if used:
            [first, *_] = client.get(
                "/api/projects", params={"integration": used["slug"], "limit": 1}
            ).json()["items"]
            detail = client.get(f"/api/projects/{first['project_id']}").json()
            assert used["slug"] in {use["slug"] for use in detail["integration_uses"]}
            assert {use["method"] for use in detail["integration_uses"]} <= {"package", "endpoint"}


def test_wrapped_team_sizes_fit_inside_the_projects():
    with TestClient(app) as client:
        body = client.get("/api/wrapped").json()
        stats = client.get("/api/stats").json()
    assert sum(item["value"] for item in body["team_sizes"]) <= stats["projects"]
    assert {item["label"] for item in body["team_sizes"]} <= {"1", "2", "3", "4", "5"}


def test_wrapped_builders_are_ranked_and_multi_team_means_two_or_more_projects():
    with TestClient(app) as client:
        body = client.get("/api/wrapped").json()
    commits = [builder["contributions"] for builder in body["top_builders"]]
    assert commits == sorted(commits, reverse=True)
    assert all(builder["projects"] >= 2 for builder in body["multi_team_builders"])
    assert not {"cursoragent", "codex"} & {b["login"] for b in body["multi_team_builders"]}


def test_agents_list_every_catalog_agent_with_a_project_count():
    with TestClient(app) as client:
        body = client.get("/api/agents").json()
        projects = client.get("/api/projects", params={"limit": 5}).json()["items"]
    assert {"claude-code", "cursor", "codex"} <= {row["slug"] for row in body}
    assert all(row["projects"] >= 0 for row in body)
    assert all(isinstance(item["agents"], list) for item in projects)
