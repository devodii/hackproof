from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from hackproof.main import app


@pytest.fixture(autouse=True)
def mock_pool_lifespan(monkeypatch):
    monkeypatch.setattr("hackproof.main.open_pool", AsyncMock())
    monkeypatch.setattr("hackproof.main.close_pool", AsyncMock())


def test_tooling_api_returns_categories(monkeypatch):
    mock_data = {
        "total_projects": 12,
        "categories": [
            {
                "category": "Ecosystem Kits & Wallets",
                "description": "Adoption of official and partner Stellar libraries and kits",
                "items": [
                    {"name": "Stellar Wallets Kit", "count": 6, "percentage": 50.0},
                    {"name": "Freighter API", "count": 4, "percentage": 33.3},
                    {"name": "OpenZeppelin Contracts", "count": 3, "percentage": 25.0},
                    {"name": "Passkey Kit", "count": 2, "percentage": 16.7},
                ],
            },
            {
                "category": "Soroban SDK Major Versions",
                "description": "Declared soroban-sdk version in Cargo.toml contracts",
                "items": [
                    {"name": "v22", "count": 8, "percentage": 66.7},
                    {"name": "v21", "count": 3, "percentage": 25.0},
                ],
            },
            {
                "category": "Stellar SDK (JS) Versions",
                "description": "Declared @stellar/stellar-sdk version in web applications",
                "items": [
                    {"name": "v14", "count": 7, "percentage": 58.3},
                    {"name": "v13", "count": 2, "percentage": 16.7},
                ],
            },
            {
                "category": "Frontend Frameworks",
                "description": "Application architecture: Next.js vs Vite vs other",
                "items": [
                    {"name": "Next.js", "count": 6, "percentage": 50.0},
                    {"name": "Vite", "count": 4, "percentage": 33.3},
                    {"name": "Other", "count": 2, "percentage": 16.7},
                ],
            },
            {
                "category": "AI Tooling & Rules",
                "description": "Agent instructions, prompts and rules present in repository trees",
                "items": [
                    {"name": "CLAUDE.md", "count": 5, "percentage": 41.7},
                    {"name": "Cursor rules", "count": 4, "percentage": 33.3},
                    {"name": "AGENTS.md", "count": 3, "percentage": 25.0},
                    {"name": "Copilot instructions", "count": 1, "percentage": 8.3},
                ],
            },
        ],
    }

    monkeypatch.setattr("hackproof.queries.fetch_tooling", AsyncMock(return_value=mock_data))

    with TestClient(app) as client:
        resp = client.get("/api/tooling")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_projects"] == 12
        assert len(body["categories"]) == 5

        categories = {cat["category"]: cat for cat in body["categories"]}
        assert "Ecosystem Kits & Wallets" in categories
        assert "Soroban SDK Major Versions" in categories
        assert "Stellar SDK (JS) Versions" in categories
        assert "Frontend Frameworks" in categories
        assert "AI Tooling & Rules" in categories

        kits = categories["Ecosystem Kits & Wallets"]["items"]
        assert any(item["name"] == "OpenZeppelin Contracts" for item in kits)
        assert any(item["name"] == "Stellar Wallets Kit" for item in kits)
