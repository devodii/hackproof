import json
from datetime import UTC, datetime

import jsonschema
import pytest
import yaml

from hackproof import schemas as api_schemas
from hackproof.export.build import build_export
from hackproof.export.files import (
    API_SCHEMA_MODELS,
    EVENT_FILE,
    EVENT_SCHEMA_FILE,
    SCHEMA_FILE,
    event_schema,
    file_names,
    file_schema,
    project_file,
    to_file_yaml,
    write_api_schemas,
    write_project_files,
)
from hackproof.hackathon import get_hackathon
from hackproof.linking.reconcile import reconcile
from tests.helpers import STELLAR, add_repo
from tests.test_export import populated_export


def keys(value):
    if isinstance(value, dict):
        return set(value) | {inner for item in value.values() for inner in keys(item)}
    if isinstance(value, list):
        return {inner for item in value for inner in keys(item)}

    return set()


async def likely_export(db, *names):
    for name in names:
        await add_repo(db, name, window_commits=7, dependencies=STELLAR)
    await reconcile(db)

    return await build_export(db, get_hackathon(), ["likely", "possible"])


async def test_a_project_file_validates_and_keeps_only_public_facts(scratch_db):
    export = await populated_export(scratch_db)
    [project] = export.projects

    text = to_file_yaml(project_file(export.hackathon.slug, project))
    data = yaml.safe_load(text)

    jsonschema.validate(data, file_schema())
    assert text.startswith("# yaml-language-server: $schema=../schema-hackathon-project.yml\n")
    assert data["canonical_id"] == "pkg:github/team/app"
    assert data["contributors"] == [{"login": "ana", "contributions": 12}]
    assert data["chain"]["accounts"] == ["GDEPLOYER"]
    assert not {"avatar_url", "country", "stars", "forks"} & keys(data)


async def test_unknown_values_are_left_out_but_unknown_versions_are_kept(scratch_db):
    export = await populated_export(scratch_db)
    [project] = export.projects
    project = project.model_copy(
        update={"description": None, "stack_versions": {"@stellar/stellar-sdk": None}}
    )

    data = yaml.safe_load(to_file_yaml(project_file("hackmeridian-2026", project)))

    assert "description" not in data
    assert data["stack"] == {"@stellar/stellar-sdk": None}


async def test_file_names_are_lowercase_with_hyphens(scratch_db):
    export = await likely_export(scratch_db, "team/Stellar_Split", "team/Hack.Pay")

    assert sorted(file_names(export.projects).values()) == ["hack-pay", "stellar-split"]


async def test_colliding_names_are_prefixed_with_the_owner(scratch_db):
    export = await likely_export(scratch_db, "ana/koul", "Bo/koul", "cy/unique")

    assert file_names(export.projects) == {
        "ana/koul": "ana-koul",
        "Bo/koul": "bo-koul",
        "cy/unique": "unique",
    }


async def test_a_name_without_letters_or_digits_is_an_error(scratch_db):
    export = await likely_export(scratch_db, "team/___")

    with pytest.raises(ValueError, match="no usable file name"):
        file_names(export.projects)


async def test_writing_files_replaces_stale_ones_and_keeps_the_event_manifest(scratch_db, tmp_path):
    export = await likely_export(scratch_db, "team/app")
    year = tmp_path / str(export.hackathon.starts_at.year)
    year.mkdir()
    (year / "gone.yml").write_text("event: old\n")

    count = write_project_files(export, tmp_path)

    assert count == 1
    assert sorted(path.name for path in year.glob("*.yml")) == [EVENT_FILE, "app.yml"]
    jsonschema.validate(yaml.safe_load((year / "app.yml").read_text()), file_schema())
    assert yaml.safe_load((tmp_path / SCHEMA_FILE).read_text())["title"] == "ProjectFile"


async def test_the_event_manifest_validates_and_names_the_event(scratch_db, tmp_path):
    export = await likely_export(scratch_db, "team/app")

    write_project_files(export, tmp_path)
    year = tmp_path / str(export.hackathon.starts_at.year)
    text = (year / EVENT_FILE).read_text()
    manifest = yaml.safe_load(text)

    jsonschema.validate(manifest, event_schema())
    assert text.startswith(f"# yaml-language-server: $schema=../{EVENT_SCHEMA_FILE}\n")
    assert manifest["slug"] == export.hackathon.slug
    assert manifest["network"] == "testnet"
    assert manifest["ends_at"] > manifest["starts_at"]


def test_api_schemas_and_index_validate_sample_responses(tmp_path):
    now = datetime(2026, 10, 12, 12, 0, tzinfo=UTC)
    sample_project = api_schemas.Project(
        project_id="repo:team/app",
        full_name="team/app",
        url="https://github.com/team/app",
        footprint="contracts",
        tier="verified",
        contracts=1,
        classic_ops=2,
        assets=0,
        builders=1,
        wasm_uploads=1,
        failed_txs=0,
        first_activity=now,
        last_activity=now,
        description="Sample project",
        homepage=None,
        stars=5,
        forks=1,
        language="Rust",
        license="MIT",
        owner="team",
        owner_avatar="https://avatars/team",
        country="US",
        dependencies=None,
        window_commits=7,
        total_commits=10,
        stellar_added_in_window=True,
        created_at=now,
        topics=["stellar"],
        track="genesis",
        integrations=["privy"],
        tools=[],
        award="first",
    )
    sample_contributor = api_schemas.Contributor(
        login="ana",
        url="https://github.com/ana",
        avatar_url="https://avatars/ana",
        contributions=12,
        country="PT",
    )
    sample_link = api_schemas.Link(
        subject_kind="contract",
        subject="CXYZ",
        method="contract_in_repo",
        path="README.md",
    )
    sample_contract = api_schemas.Contract(
        contract_id="CXYZ",
        deployer="GDEPLOYER",
        wasm_hash="w1",
        tx_hash="tx1",
        ledger=100,
        deployed_at=now,
        project_id="repo:team/app",
    )
    sample_wasm = api_schemas.WasmUpload(
        wasm_hash="w1",
        uploader="GDEPLOYER",
        tx_hash="tx1",
        size=1024,
        source_repo="team/app",
        full_name="team/app",
        contracts=1,
        uploaded_at=now,
    )
    sample_failed = api_schemas.FailedTx(
        tx_hash="tx_fail",
        source_account="GDEPLOYER",
        kind="soroban",
        result_code="tx_failed",
        ledger=101,
        created_at=now,
    )
    sample_integration_use = api_schemas.IntegrationUse(
        slug="privy",
        name="Privy",
        method="package",
        evidence="@privy-io/node",
        path="package.json",
    )
    samples = {
        "stats": api_schemas.Stats(
            projects=10,
            verified_projects=5,
            likely_projects=3,
            possible_projects=2,
            unattributed_accounts=1,
            contracts=8,
            builders=6,
            contributors=15,
            countries=4,
            wasm_uploads=9,
            failed_txs=2,
        ),
        "project": sample_project,
        "contributor": sample_contributor,
        "link": sample_link,
        "contract": sample_contract,
        "wasm-upload": sample_wasm,
        "failed-tx": sample_failed,
        "integration-use": sample_integration_use,
        "project-detail": api_schemas.ProjectDetail(
            project=sample_project,
            links=[sample_link],
            integration_uses=[sample_integration_use],
            tool_uses=[],
            contributors=[sample_contributor],
            contracts=[sample_contract],
            wasm_uploads=[sample_wasm],
            failed_txs=[sample_failed],
        ),
        "builder": api_schemas.Builder(
            address="GDEPLOYER",
            projects=[sample_project],
            contracts=[sample_contract],
            wasm_uploads=[sample_wasm],
            failed_txs=[sample_failed],
        ),
        "timeline-point": api_schemas.TimelinePoint(hour=now, contracts=3),
        "integration": api_schemas.Integration(
            slug="privy",
            name="Privy",
            category="wallets",
            site="https://privy.io",
            projects=4,
        ),
        "ecosystem-tool": api_schemas.EcosystemTool(
            slug="scaffold-stellar",
            name="Scaffold Stellar",
            site="https://scaffoldstellar.org",
            projects=6,
        ),
        "country-count": api_schemas.CountryCount(country="PT", contributors=3),
        "project-page": api_schemas.Page[api_schemas.Project](items=[sample_project], total=1),
        "contract-page": api_schemas.Page[api_schemas.Contract](items=[sample_contract], total=1),
        "wasm-upload-page": api_schemas.Page[api_schemas.WasmUpload](items=[sample_wasm], total=1),
        "failed-tx-page": api_schemas.Page[api_schemas.FailedTx](items=[sample_failed], total=1),
    }

    index = write_api_schemas(tmp_path)
    loaded_index = json.loads((tmp_path / "index.json").read_text())
    assert loaded_index == index
    indexed_names = {entry["name"] for entry in loaded_index["schemas"]}
    assert {"hackathon-export", "hackathon-project", "event"} <= indexed_names

    for slug, _ in API_SCHEMA_MODELS:
        schema_path = tmp_path / f"{slug}.schema.json"
        schema = json.loads(schema_path.read_text())
        assert schema["$id"].endswith(f"/{slug}.schema.json")
        assert schema["version"] == "1.0"
        jsonschema.validate(samples[slug].model_dump(mode="json"), schema)
