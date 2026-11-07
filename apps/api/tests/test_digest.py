from hackproof.digest import collect_snapshot, post_or_print_digest, render_digest


def test_two_weekly_runs_produce_a_deterministic_digest_and_skip_missing_sections():
    run_1 = {
        "projects": {"verified": 42, "likely": 18, "contracts": 65},
        "survival": {"active": 30, "total": 60},
    }
    run_2 = {
        "projects": {"verified": 45, "likely": 17, "contracts": 70},
        "survival": {"active": 28, "total": 62},
    }

    digest_a = render_digest(run_1, run_2)
    digest_b = render_digest(run_1, run_2)

    assert digest_a == digest_b
    assert digest_a == (
        "# HackProof Weekly Digest\n\n"
        "## Projects & Chain\n"
        "- Verified projects: 45 (+3)\n"
        "- Likely projects: 17 (-1)\n"
        "- Deployed contracts: 70 (+5)\n\n"
        "## Survival\n"
        "- Active repos: 28 (-2)\n"
        "- Total tracked: 62 (+2)\n"
    )
    assert "Mainnet Graduations" not in digest_a
    assert "SCF Links" not in digest_a


async def test_collect_snapshot_skips_tables_that_do_not_exist(scratch_db):
    snapshot = await collect_snapshot(scratch_db)
    assert "projects" in snapshot
    assert "survival" not in snapshot
    assert "graduations" not in snapshot
    assert "scf_links" not in snapshot


async def test_digest_prints_when_webhook_is_unset(monkeypatch, capsys):
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("HACKPROOF_DISCORD_WEBHOOK_URL", raising=False)
    await post_or_print_digest("# HackProof Weekly Digest\n")
    assert capsys.readouterr().out == "# HackProof Weekly Digest\n"
