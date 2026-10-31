from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hackproof.digest import (
    RunSnapshot,
    generate_digest,
    load_runs_from_fixture,
    post_to_discord,
    run_digest_job,
)


def test_generate_digest_from_fixture():
    fixture_path = Path(__file__).parent / "fixtures" / "weekly_runs.json"
    prev, curr = load_runs_from_fixture(fixture_path)

    digest = generate_digest(prev, curr)

    assert "# 🚀 HackProof Weekly Digest (2026-10-25)" in digest
    assert "- **Projects**: 65 (+15 this week)" in digest
    assert "- **Contracts**: 45 (+15 this week)" in digest
    assert "- **Builders**: 54 (+12 this week)" in digest
    assert "- **Failed Txs**: 8 (+3 this week)" in digest

    # Check top movers
    assert "### ⭐ Top Survival Movers" in digest
    assert "- **repo:troqpay/private-yield**: 60 pts (+60 pts)" in digest
    assert "- **repo:ethan-r13n/nest**: 140 pts (+40 pts)" in digest
    assert "- **repo:0xDanomite/alloy-stellar**: 115 pts (+35 pts)" in digest

    # Check graduations
    assert "### 🎓 New Graduations" in digest
    assert "- **Nest**: deployed to mainnet (contract CABC123)" in digest

    # Check SCF links
    assert "### 🏆 SCF Highlights" in digest
    assert "- **Alloy Stellar**: [Round 31] funded - $25,000 USDC" in digest


def test_generate_digest_skips_missing_tables():
    prev = RunSnapshot(
        run_id="run-01",
        timestamp=datetime(2026, 10, 18, 12, 0, tzinfo=UTC),
        projects_count=10,
        contracts_count=5,
        builders_count=8,
        failed_txs_count=1,
    )
    curr = RunSnapshot(
        run_id="run-02",
        timestamp=datetime(2026, 10, 25, 12, 0, tzinfo=UTC),
        projects_count=12,
        contracts_count=7,
        builders_count=10,
        failed_txs_count=1,
    )

    digest = generate_digest(prev, curr)

    assert "# 🚀 HackProof Weekly Digest (2026-10-25)" in digest
    assert "- **Projects**: 12 (+2 this week)" in digest
    assert "- **Contracts**: 7 (+2 this week)" in digest
    assert "- **Failed Txs**: 1 (0 this week)" in digest

    # Assert non-existent tables are cleanly skipped
    assert "### ⭐ Top Survival Movers" not in digest
    assert "### 🎓 New Graduations" not in digest
    assert "### 🏆 SCF Highlights" not in digest


@pytest.mark.asyncio
async def test_post_to_discord():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        ok = await post_to_discord("Test content", "https://discord.com/api/webhooks/test/123")
        assert ok is True
        mock_post.assert_awaited_once_with(
            "https://discord.com/api/webhooks/test/123",
            json={"content": "Test content"},
        )


@pytest.mark.asyncio
async def test_run_digest_job():
    fixture_path = Path(__file__).parent / "fixtures" / "weekly_runs.json"
    digest = await run_digest_job(fixture_path=fixture_path)
    assert "# 🚀 HackProof Weekly Digest" in digest
    assert "Projects**: 65" in digest
