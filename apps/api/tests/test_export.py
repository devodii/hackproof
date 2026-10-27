from datetime import timedelta

import jsonschema
import yaml

from hackproof.export.build import build_export
from hackproof.export.render import json_schema, to_json, to_yaml
from hackproof.hackathon import get_hackathon
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
    assert project.created_during_hack is True
    assert project.contributors[0].login == "ana" and project.contributors[0].country == "PT"
    assert [c.contract_id for c in project.chain.contracts] == ["CXYZ"]
    assert project.chain.accounts == ["GDEPLOYER"]
    assert project.chain.wasm_hashes == ["w1"]
    assert [(e.method, e.subject) for e in project.chain.evidence] == [("contract_in_repo", "CXYZ")]


async def test_json_and_yaml_exports_validate_against_the_published_schema(scratch_db):
    export = await populated_export(scratch_db)
    schema = json_schema()

    jsonschema.validate(yaml.safe_load(to_yaml(export)), schema)
    jsonschema.validate(__import__("json").loads(to_json(export)), schema)


async def test_weak_tiers_are_left_out_by_default(scratch_db):
    db = scratch_db
    await add_repo(db, "weak/repo", window_commits=5, dependencies=STELLAR)
    await reconcile(db)

    assert (await build_export(db, get_hackathon())).projects == []
    everything = await build_export(db, get_hackathon(), ["possible"])
    assert [p.repo_full_name for p in everything.projects] == ["weak/repo"]
