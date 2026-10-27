from datetime import timedelta

import asyncpg

from hackproof.config import get_settings
from hackproof.hackathon import get_hackathon
from hackproof.linking.reconcile import MAX_REPOS_PER_ACCOUNT, reconcile

WINDOW = get_hackathon().window
INSIDE = WINDOW.start + timedelta(hours=3)
FRIENDBOT = get_settings().friendbot_account


async def add_repo(db: asyncpg.Connection, full_name: str, **fields: object) -> None:
    values = {"url": f"https://github.com/{full_name}", "owner": full_name.split("/")[0], **fields}
    columns = ", ".join(["full_name", *values])
    marks = ", ".join(f"${n}" for n in range(1, len(values) + 2))
    await db.execute(f"INSERT INTO repos ({columns}) VALUES ({marks})", full_name, *values.values())


async def add_ref(db: asyncpg.Connection, full_name: str, kind: str, value: str) -> None:
    await db.execute(
        "INSERT INTO repo_refs VALUES ($1, $2, $3, 'README.md')", full_name, kind, value
    )


async def add_contract(db: asyncpg.Connection, contract: str, deployer: str, wasm: str) -> None:
    await db.execute(
        "INSERT INTO contracts VALUES ($1, $2, $3, $4, 1, $5)",
        contract, deployer, wasm, f"tx-{contract}", INSIDE,
    )  # fmt: skip


async def add_upload(db: asyncpg.Connection, wasm: str, uploader: str, repo: str | None = None):
    await db.execute(
        "INSERT INTO wasm_uploads VALUES ($1, $2, $3, 10, $4, '{}', 1, $5)",
        f"up-{wasm}-{uploader}", wasm, uploader, repo, INSIDE,
    )  # fmt: skip


async def add_funding(db: asyncpg.Connection, account: str) -> None:
    await db.execute(
        "INSERT INTO accounts VALUES ($1, $2, $3, 1, $4)",
        account,
        FRIENDBOT,
        f"fund-{account}",
        INSIDE,
    )


async def links(db: asyncpg.Connection) -> dict[tuple[str, str, str], str]:
    rows = await db.fetch("SELECT full_name, subject_kind, subject, method FROM links")
    return {(r["full_name"], r["subject_kind"], r["subject"]): r["method"] for r in rows}


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
    await add_repo(db, "team/payments", window_commits=9, mentions_hackathon=True,
                   dependencies='{"ecosystems": ["js"], "packages": {}}')  # fmt: skip
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
