from datetime import timedelta

from hackproof.linking.reconcile import MAX_REPOS_PER_ACCOUNT, reconcile
from tests.helpers import (
    INSIDE,
    STELLAR,
    WINDOW,
    add_contract,
    add_funding,
    add_ref,
    add_repo,
    add_upload,
    links,
    tiers,
)


async def test_a_contract_in_a_repo_pulls_in_the_whole_deployer_footprint(scratch_db):
    db = scratch_db
    await add_repo(db, "team/app", window_commits=5)
    await add_ref(db, "team/app", "contract", "C1")
    await add_contract(db, "C1", "GDEPLOYER", "w1")
    await add_contract(db, "C2", "GDEPLOYER", "w2")

    await reconcile(db)

    found = await links(db)
    assert found[("team/app", "contract", "C1")] == "contract_in_repo"
    assert found[("team/app", "account", "GDEPLOYER")] == "footprint"
    assert found[("team/app", "contract", "C2")] == "footprint"
    project = await db.fetchrow("SELECT * FROM projects WHERE project_id = 'repo:team/app'")
    assert (project["contracts"], project["footprint"], project["builders"]) == (2, "contracts", 1)


async def test_wasm_metadata_links_regardless_of_repo_name_case(scratch_db):
    db = scratch_db
    await add_repo(db, "Team/App")
    await add_upload(db, "w1", "GDEPLOYER", repo="github:team/app")
    await add_contract(db, "C1", "GDEPLOYER", "w1")

    await reconcile(db)

    found = await links(db)
    assert found[("Team/App", "wasm", "w1")] == "wasm_meta"
    assert found[("Team/App", "contract", "C1")] == "footprint"


async def test_a_shared_template_wasm_does_not_merge_unrelated_teams(scratch_db):
    db = scratch_db
    await add_repo(db, "stellar-scaffold/cli")
    await add_upload(db, "template", "GTEAMA", repo="github:stellar-scaffold/cli")
    await add_upload(db, "template", "GTEAMB")
    await add_contract(db, "CA", "GTEAMA", "template")
    await add_contract(db, "CB", "GTEAMB", "template")

    await reconcile(db)

    found = await links(db)
    assert ("stellar-scaffold/cli", "wasm", "template") in found
    assert not any(kind in ("account", "contract") for _, kind, _ in found)


async def test_hacker_accounts_in_a_repo_attach_a_contractless_project(scratch_db):
    db = scratch_db
    await add_repo(db, "team/payments", window_commits=9,
                   dependencies={"ecosystems": ["js"], "packages": {}})  # fmt: skip
    await add_funding(db, "GHACKER")
    await add_ref(db, "team/payments", "account", "GHACKER")
    await db.execute(
        "INSERT INTO classic_ops VALUES ('t', 0, 'GHACKER', 'payment', NULL, NULL, 1, $1)", INSIDE
    )

    await reconcile(db)

    assert (await links(db))[("team/payments", "account", "GHACKER")] == "deployer_in_repo"
    project = await db.fetchrow("SELECT * FROM projects WHERE project_id = 'repo:team/payments'")
    assert (project["footprint"], project["classic_ops"]) == ("classic", 1)


async def test_accounts_referenced_everywhere_are_treated_as_infrastructure(scratch_db):
    db = scratch_db
    await add_funding(db, "GFAUCET")
    for number in range(MAX_REPOS_PER_ACCOUNT + 1):
        await add_repo(db, f"team/app{number}")
        await add_ref(db, f"team/app{number}", "account", "GFAUCET")

    await reconcile(db)

    assert await links(db) == {}


async def test_unattributed_deployers_become_account_projects(scratch_db):
    db = scratch_db
    await add_contract(db, "C1", "GLONE", "w1")

    report = await reconcile(db)

    assert report.projects_by_footprint == {"contracts": 1}
    assert await db.fetchval("SELECT project_id FROM projects") == "acct:GLONE"


async def test_older_repos_that_added_stellar_during_the_window_become_projects(scratch_db):
    db = scratch_db
    await add_repo(db, "team/old", stellar_added_in_window=True, dependencies=STELLAR)
    await add_repo(db, "team/stale", stellar_added_in_window=False, dependencies=STELLAR)

    await reconcile(db)

    ids = {row["project_id"] for row in await db.fetch("SELECT project_id FROM projects")}
    assert ids == {"repo:team/old"}


async def test_repos_created_inside_the_window_become_projects(scratch_db):
    db = scratch_db
    await add_repo(db, "team/new", created_at=INSIDE, dependencies=STELLAR)

    await reconcile(db)

    assert await db.fetchval("SELECT project_id FROM projects") == "repo:team/new"


async def test_projects_are_tiered_by_how_strong_the_hackmeridian_evidence_is(scratch_db):
    db = scratch_db
    await add_repo(db, "a/chain", window_commits=1)
    await add_ref(db, "a/chain", "contract", "C1")
    await add_contract(db, "C1", "GCHAIN", "w1")
    await add_repo(db, "c/likely", window_commits=2, created_at=INSIDE, dependencies=STELLAR)
    await add_repo(db, "d/possible", window_commits=5, dependencies=STELLAR)

    await reconcile(db)

    assert await tiers(db) == {
        "repo:a/chain": "verified",
        "repo:c/likely": "likely",
        "repo:d/possible": "possible",
    }


async def test_matches_that_only_touch_the_pre_start_margin_are_not_verified(scratch_db):
    db = scratch_db
    await add_repo(db, "team/early", window_commits=1)
    await add_ref(db, "team/early", "contract", "C1")
    await db.execute(
        "INSERT INTO contracts VALUES ('C1', 'GEARLY', 'w1', 'tx', 1, $1)",
        WINDOW.start - timedelta(minutes=30),
    )

    await reconcile(db)

    assert (await links(db))[("team/early", "contract", "C1")] == "contract_in_repo"
    assert (await tiers(db))["repo:team/early"] == "possible"


async def test_a_chain_item_matched_by_two_repos_is_credited_to_the_older_one(scratch_db):
    db = scratch_db
    for name, created in (("team/copy", INSIDE), ("team/original", INSIDE - timedelta(days=30))):
        await add_repo(db, name, window_commits=3, created_at=created)
        await add_ref(db, name, "contract", "C1")
    await add_contract(db, "C1", "GDEPLOYER", "w1")

    await reconcile(db)
    first = await db.fetchval("SELECT full_name FROM attribution WHERE subject = 'C1'")
    await reconcile(db)
    second = await db.fetchval("SELECT full_name FROM attribution WHERE subject = 'C1'")

    assert first == second == "team/original"
