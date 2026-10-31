from datetime import UTC, datetime

import jsonschema

from hackproof.export.atlas import atlas_json_schema, export_atlas, map_project_to_atlas
from hackproof.export.diff import compute_diff
from hackproof.export.models import (
    Chain,
    Contract,
    Contributor,
    Evidence,
    Owner,
    Project,
    WasmUpload,
)
from hackproof.export.stellarlight import (
    export_stellarlight,
    map_project_to_stellarlight,
    stellarlight_json_schema,
)


def _sample_project(
    repo_full_name: str = "sample-org/stellar-app",
    name: str = "stellar-app",
    tier: str = "verified",
    award: str | None = "first",
) -> Project:
    now = datetime(2026, 10, 25, 12, 0, tzinfo=UTC)
    return Project(
        repo_full_name=repo_full_name,
        name=name,
        repo_url=f"https://github.com/{repo_full_name}",
        description="A decentralized app on Soroban",
        homepage="https://stellar-app.example.com",
        tier=tier,
        track="genesis",
        award=award,
        language="Rust",
        license="Apache-2.0",
        stars=42,
        forks=5,
        self_tags=["stellar", "soroban"],
        stack=["soroban-sdk"],
        stack_versions={"soroban-sdk": "22.0.0"},
        repo_created_at=now,
        repo_last_commit_at=now,
        commits_in_window=10,
        total_commits=15,
        integration_partners=[],
        owner=Owner(login="sample-org", avatar_url=None, country="US"),
        contributors=[
            Contributor(
                login="alice",
                url="https://github.com/alice",
                avatar_url=None,
                contributions=8,
                country="US",
            ),
            Contributor(
                login="bob",
                url="https://github.com/bob",
                avatar_url=None,
                contributions=2,
                country="PT",
            ),
        ],
        chain=Chain(
            contract_count=1,
            wasm_upload_count=1,
            classic_op_count=0,
            asset_count=0,
            failed_tx_count=0,
            accounts=[],
            wasm_uploads=[
                WasmUpload(
                    wasm_hash="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    upload_tx="tx123",
                    explorer_url="https://stellar.expert/tx/tx123",
                )
            ],
            contracts=[
                Contract(
                    contract_id="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    deployer="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    wasm_hash="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                    deployed_at=now,
                    ledger=123456,
                    tx_hash="txdeploy123",
                    explorer_url="https://stellar.expert/contract/CAAA",
                    tx_url="https://stellar.expert/tx/txdeploy123",
                )
            ],
            evidence=[
                Evidence(
                    kind="contract",
                    subject="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    method="contract_in_repo",
                    explorer_url="https://stellar.expert/contract/CAAA",
                    repo_file_url="https://github.com/sample-org/stellar-app/blob/main/config.json",
                )
            ],
        ),
    )


def test_stellarlight_mapping_and_schema_validation():
    project = _sample_project()
    event_slug = "hackmeridian-2026"

    row = map_project_to_stellarlight(project, event_slug)
    assert row.id == "repo:sample-org/stellar-app"
    assert row.event == "hackmeridian-2026"
    assert row.name == "stellar-app"
    assert row.tagline == "A decentralized app on Soroban"
    assert row.repo == "https://github.com/sample-org/stellar-app"
    assert row.repo_verified is True
    assert row.official_status == "first"
    assert "alice" in row.builders
    assert "bob" in row.builders
    assert any(
        "CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" in ev
        for ev in row.verification_evidence
    )

    # Acceptance criteria: Validate every exported row against its schema
    exported_data = export_stellarlight([project], event_slug)
    schema = stellarlight_json_schema()
    jsonschema.validate(instance=exported_data, schema=schema)


def test_atlas_mapping_and_schema_validation():
    project = _sample_project()
    program_name = "HackMeridian 2026"

    row = map_project_to_atlas(project, program_name)
    assert row.repo == "https://github.com/sample-org/stellar-app"
    assert row.project == "stellar-app"
    assert row.program == "HackMeridian 2026"
    assert row.person_or_org == "sample-org"
    assert row.language == "Rust"
    assert "CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" in row.chain_evidence

    # Acceptance criteria: Validate every exported row against its schema
    exported_data = export_atlas([project], program_name)
    schema = atlas_json_schema()
    jsonschema.validate(instance=exported_data, schema=schema)


def test_diff_computation():
    old_data = [
        {"id": "p1", "name": "Project 1"},
        {"id": "p2", "name": "Project 2 (old)"},
    ]
    new_data = [
        {"id": "p2", "name": "Project 2 (new)"},
        {"id": "p3", "name": "Project 3"},
    ]

    res = compute_diff(old_data, new_data, key_field="id", target_name="TestTarget")
    assert res["added"] == 1
    assert res["removed"] == 1
    assert res["modified"] == 1
