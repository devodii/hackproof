from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from hackproof.chat.tools import run_tool
from hackproof.config import Settings
from hackproof.export.files import write_project_files
from hackproof.export.models import Chain, HackathonExport, Owner, Project
from hackproof.export.models import Hackathon as ExportedHackathon
from hackproof.hackathon import Discovery, Hackathon, Window, hidden_ids
from hackproof.main import app
from hackproof.queries import is_hidden, list_page


@pytest.fixture(autouse=True)
def mock_pool_lifespan(monkeypatch):
    monkeypatch.setattr("hackproof.main.open_pool", AsyncMock())
    monkeypatch.setattr("hackproof.main.close_pool", AsyncMock())


def make_hackathon(hidden: list[str] | None = None) -> Hackathon:
    now = datetime.now(UTC)
    return Hackathon(
        slug="test-hack",
        name="Test Hack",
        window=Window(start=now, pull_start=now, end=now),
        discovery=Discovery(
            github_queries=[],
            github_code_queries=[],
            github_string_queries=[],
            dependency_fingerprints={},
            exclude_owners=[],
            known_infra_accounts=[],
        ),
        hidden=hidden or [],
    )


def test_hackathon_hidden_defaults_and_normalizes(monkeypatch):
    h = make_hackathon(hidden=["repo:owner/app", "plain/name", "acct:G123"])
    monkeypatch.setattr("hackproof.hackathon.get_hackathon", lambda: h)

    ids = hidden_ids()
    assert "owner/app" in ids
    assert "repo:owner/app" in ids
    assert "plain/name" in ids
    assert "repo:plain/name" in ids
    assert "acct:G123" in ids


def test_is_hidden_detection(monkeypatch):
    h = make_hackathon(hidden=["repo:secret/repo", "GDEPLOYER"])
    monkeypatch.setattr("hackproof.hackathon.get_hackathon", lambda: h)

    assert is_hidden("secret/repo")
    assert is_hidden("repo:secret/repo")
    assert is_hidden("GDEPLOYER")
    assert is_hidden("acct:GDEPLOYER")
    assert not is_hidden("public/repo")
    assert not is_hidden("GPUBLIC")


def test_opt_out_endpoint_validates_input():
    with TestClient(app) as client:
        resp = client.post("/api/opt-out", json={"project_id": "", "handle": ""})
        assert resp.status_code == 400

        resp2 = client.post("/api/opt-out", json={"project_id": "repo:a/b", "handle": ""})
        assert resp2.status_code == 400


def test_opt_out_endpoint_creates_github_issue(monkeypatch):
    mock_resp = AsyncMock()
    mock_resp.status_code = 201
    mock_resp.json = lambda: {"html_url": "https://github.com/devodii/hackproof/issues/999"}
    mock_post = AsyncMock(return_value=mock_resp)

    test_settings = Settings(
        opt_out_github_token="fake-token",
        github_tokens=["token1"],
    )
    monkeypatch.setattr("hackproof.routes.get_settings", lambda: test_settings)
    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    with TestClient(app) as client:
        res = client.post(
            "/api/opt-out",
            json={
                "project_id": "repo:privacy/project",
                "handle": "private_builder",
                "reason": "Requesting project removal",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "We honor opt outs within 24h." in data["message"]
        assert data["issue_url"] == "https://github.com/devodii/hackproof/issues/999"

        # Verify call arguments
        assert mock_post.called
        kwargs = mock_post.call_args.kwargs
        assert "opt-out" in kwargs["json"]["labels"]
        assert "Opt out request: repo:privacy/project" in kwargs["json"]["title"]
        assert "@private_builder" in kwargs["json"]["body"]
        assert "We honor opt outs within 24h." in kwargs["json"]["body"]


async def test_hidden_id_never_appears_in_api_response(monkeypatch):
    h = make_hackathon(hidden=["repo:stealth/app", "GSTEALTH"])
    monkeypatch.setattr("hackproof.hackathon.get_hackathon", lambda: h)

    with TestClient(app) as client:
        # 1. Project detail endpoint returns 404 for hidden project
        resp = client.get("/api/projects/repo:stealth/app")
        assert resp.status_code == 404

        # 2. Builder detail endpoint returns 404 for hidden account
        resp_builder = client.get("/api/builders/GSTEALTH")
        assert resp_builder.status_code == 404

    # 3. Direct queries.list_page returns empty
    items, total = await list_page("projects", project_id="repo:stealth/app")
    assert items == []
    assert total == 0

    items_c, total_c = await list_page("contracts", project_id="repo:stealth/app")
    assert items_c == []
    assert total_c == 0

    items_b, total_b = await list_page("projects", account="GSTEALTH")
    assert items_b == []
    assert total_b == 0


def test_hidden_id_never_appears_in_export(tmp_path: Path):
    now = datetime.now(UTC)
    export_hack = ExportedHackathon(
        slug="test-hack",
        name="Test Hack",
        network="testnet",
        starts_at=now,
        submission_deadline=now,
    )
    p_visible = Project(
        repo_full_name="public/app",
        repo_url="https://github.com/public/app",
        name="app",
        description="Public app",
        homepage=None,
        tier="verified",
        track="genesis",
        track_declared=True,
        award=None,
        language="Rust",
        license="MIT",
        stars=10,
        forks=2,
        self_tags=["stellar"],
        stack=["@stellar/stellar-sdk"],
        stack_versions={"@stellar/stellar-sdk": "14.0.0"},
        repo_created_at=now,
        repo_last_commit_at=now,
        commits_in_window=5,
        total_commits=10,
        owner=Owner(login="public_user", avatar_url=None, country=None),
        chain=Chain(
            contract_count=1,
            wasm_upload_count=1,
            classic_op_count=0,
            asset_count=0,
            failed_tx_count=0,
            accounts=[],
            wasm_uploads=[],
            contracts=[],
            evidence=[],
        ),
        contributors=[],
        integration_partners=[],
    )
    export = HackathonExport(hackathon=export_hack, projects=[p_visible])

    # Write files
    written = write_project_files(export, tmp_path)
    assert written == 1

    # Check that stealth/app YAML was never generated
    generated_files = [f.name for f in tmp_path.glob("**/*.yml")]
    assert any("app.yml" in f for f in generated_files)
    assert not any("stealth" in f for f in generated_files)


async def test_hidden_id_never_appears_in_chat_tools(monkeypatch):
    h = make_hackathon(hidden=["repo:stealth/app", "GSTEALTH"])
    monkeypatch.setattr("hackproof.hackathon.get_hackathon", lambda: h)

    # 1. get_project returns error when hidden
    res = await run_tool("get_project", {"project_id": "repo:stealth/app"})
    assert res == {"error": "project not found"}

    # 2. get_builder returns error when hidden
    res_b = await run_tool("get_builder", {"address": "GSTEALTH"})
    assert res_b == {"error": "no activity in the hack window"}

    # 3. query_contracts with hidden project_id returns empty
    res_c = await run_tool("query_contracts", {"project_id": "repo:stealth/app"})
    assert res_c["total"] == 0
    assert res_c["items"] == []
