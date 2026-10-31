from datetime import timedelta

from hackproof.export.build import build_export
from hackproof.export.urls import EXPLORER
from hackproof.hackathon import Award, get_hackathon
from hackproof.linking.reconcile import reconcile
from tests.helpers import STELLAR, WINDOW, add_contract, add_ref, add_repo, add_upload


async def populated_export(db):
    await add_repo(
        db,
        "team/app",
        description="An app",
        window_commits=7,
        total_commits=9,
        stars=3,
        topics=["stellar"],
        owner_avatar="https://avatars/team",
        created_at=WINDOW.start + timedelta(hours=1),
        dependencies=STELLAR,
    )
    await add_ref(db, "team/app", "contract", "CXYZ")
    await add_contract(db, "CXYZ", "GDEPLOYER", "w1")
    await add_upload(db, "w1", "GDEPLOYER")
    await db.execute(
        "INSERT INTO repo_contributors VALUES ('team/app', 'ana', 'https://github.com/ana', "
        "'https://avatars/ana', 12)"
    )
    await db.execute(
        "INSERT INTO github_users (login, location, country) VALUES ('ana', 'x', 'PT')"
    )
    await reconcile(db)
    return await build_export(db, get_hackathon())


async def test_export_carries_repo_chain_and_evidence(scratch_db):
    export = await populated_export(scratch_db)

    [project] = export.projects
    assert (project.repo_full_name, project.tier, project.name) == ("team/app", "verified", "app")
    assert project.stack == ["@stellar/stellar-sdk"]
    assert project.track == "genesis"
    assert project.contributors[0].login == "ana" and project.contributors[0].country == "PT"
    assert [c.contract_id for c in project.chain.contracts] == ["CXYZ"]
    assert [a.address for a in project.chain.accounts] == ["GDEPLOYER"]
    assert project.chain.accounts[0].explorer_url == f"{EXPLORER}/account/GDEPLOYER"
    assert [w.wasm_hash for w in project.chain.wasm_uploads] == ["w1"]
    [contract] = project.chain.contracts
    assert contract.explorer_url == f"{EXPLORER}/contract/CXYZ"
    assert contract.tx_url == f"{EXPLORER}/tx/{contract.tx_hash}"
    [evidence] = project.chain.evidence
    assert (evidence.method, evidence.subject) == ("contract_in_repo", "CXYZ")
    assert evidence.explorer_url == f"{EXPLORER}/contract/CXYZ"
    assert evidence.repo_file_url == "https://github.com/team/app/blob/HEAD/README.md"


async def test_weak_tiers_are_left_out_by_default(scratch_db):
    db = scratch_db
    await add_repo(db, "weak/repo", window_commits=5, dependencies=STELLAR)
    await reconcile(db)

    assert (await build_export(db, get_hackathon())).projects == []
    everything = await build_export(db, get_hackathon(), ["possible"])
    assert [p.repo_full_name for p in everything.projects] == ["weak/repo"]


async def test_track_is_the_declared_one_and_genesis_otherwise(scratch_db):
    db = scratch_db
    await add_repo(
        db,
        "team/declared",
        window_commits=4,
        created_at=WINDOW.start - timedelta(days=90),
        stellar_added_in_window=True,
        declared_track="scale",
        dependencies=STELLAR,
    )
    await add_repo(
        db,
        "team/silent",
        window_commits=4,
        created_at=WINDOW.start + timedelta(hours=1),
        dependencies=STELLAR,
    )
    await reconcile(db)

    projects = (await build_export(db, get_hackathon(), ["likely", "possible"])).projects

    assert {p.repo_full_name: (p.track, p.track_declared) for p in projects} == {
        "team/declared": ("scale", True),
        "team/silent": ("genesis", False),
    }


async def test_export_lists_integration_partners_with_their_evidence(scratch_db):
    db = scratch_db
    await add_repo(db, "team/app", window_commits=7, dependencies=STELLAR)
    await add_ref(db, "team/app", "contract", "CXYZ")
    await add_contract(db, "CXYZ", "GDEPLOYER", "w1")
    await db.executemany(
        "INSERT INTO repo_integrations VALUES ('team/app', $1, $2, $3, $4)",
        [
            ("privy", "package", "@privy-io/node", "package.json"),
            ("trustless-work", "endpoint", "api.trustlesswork.com", "src/client.go"),
        ],
    )
    await reconcile(db)

    [project] = (await build_export(db, get_hackathon())).projects

    assert [p.slug for p in project.integration_partners] == ["trustless-work", "privy"]
    [evidence] = project.integration_partners[0].evidence
    assert (evidence.method, evidence.detail) == ("endpoint", "api.trustlesswork.com")
    assert evidence.repo_file_url == "https://github.com/team/app/blob/HEAD/src/client.go"


async def test_export_marks_award_winners(scratch_db):
    db = scratch_db
    await add_repo(db, "team/winner", window_commits=7, dependencies=STELLAR)
    await add_repo(db, "team/other", window_commits=7, dependencies=STELLAR)
    await reconcile(db)
    hackathon = get_hackathon().model_copy(
        update={"awards": [Award(project_id="repo:team/winner", place="first")]}
    )

    projects = (await build_export(db, hackathon, ["likely", "possible"])).projects

    assert {p.repo_full_name: p.award for p in projects} == {
        "team/winner": "first",
        "team/other": None,
    }
