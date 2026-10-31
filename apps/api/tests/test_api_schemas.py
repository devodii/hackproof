import json
from datetime import UTC, datetime

import jsonschema

from hackproof.export.jobs import PUBLIC, export_schemas
from hackproof.export.render import API_MODELS, API_SCHEMA_VERSION
from hackproof.github.models import DependencyFingerprint
from hackproof.schemas import (
    Builder,
    Contract,
    Contributor,
    CountryCount,
    FailedTx,
    Integration,
    IntegrationUse,
    Link,
    Project,
    ProjectDetail,
    Stats,
    TimelinePoint,
    WasmUpload,
)


def test_schema_index_lists_existing_export_and_api_versions():
    export_schemas()
    index_file = PUBLIC / "schema" / "index.json"
    assert index_file.exists()

    index_data = json.loads(index_file.read_text(encoding="utf-8"))
    assert "$schema" in index_data
    assert index_data.get("name") == "HackProof Schema Index"

    schemas_by_name = {s["name"]: s for s in index_data["schemas"]}

    # Verify export schema versions are listed
    assert "hackathon-export" in schemas_by_name
    export_meta = schemas_by_name["hackathon-export"]
    assert export_meta["versions"] == ["1.0", "1.1", "1.2"]
    assert export_meta["latest"] == "1.2"
    for file in export_meta["files"]:
        assert (PUBLIC / "schema" / file).exists()

    # Verify every API model is listed
    for slug, model in API_MODELS.items():
        assert slug in schemas_by_name
        entry = schemas_by_name[slug]
        assert entry["model"] == model.__name__
        assert entry["versions"] == [API_SCHEMA_VERSION]
        assert (PUBLIC / "schema" / f"{slug}-{API_SCHEMA_VERSION}.schema.json").exists()


def test_api_models_validate_against_their_schemas():
    export_schemas()
    now = datetime(2026, 10, 31, 12, 0, 0, tzinfo=UTC)

    # Representative sample instances for each model
    sample_stats = Stats(
        projects=10,
        verified_projects=5,
        likely_projects=3,
        possible_projects=2,
        unattributed_accounts=1,
        contracts=8,
        builders=12,
        contributors=15,
        countries=6,
        wasm_uploads=9,
        failed_txs=1,
    )

    sample_project = Project(
        project_id="repo:stellar/wallet",
        full_name="stellar/wallet",
        url="https://github.com/stellar/wallet",
        footprint="contracts",
        tier="verified",
        contracts=2,
        classic_ops=10,
        assets=1,
        builders=3,
        wasm_uploads=2,
        failed_txs=0,
        first_activity=now,
        last_activity=now,
        description="A stellar testnet wallet",
        homepage="https://wallet.stellar.org",
        stars=42,
        forks=5,
        language="TypeScript",
        license="MIT",
        owner="stellar",
        owner_avatar="https://avatars.githubusercontent.com/u/1",
        country="PT",
        dependencies=DependencyFingerprint(
            stellar_packages=["@stellar/stellar-sdk"],
            network_strings=["testnet.stellar.org"],
            soroban_imports=[],
            wasm_references=[],
        ),
        window_commits=14,
        total_commits=35,
        stellar_added_in_window=True,
        created_at=now,
        topics=["stellar", "soroban"],
        track="genesis",
        integrations=["privy"],
        award="first",
    )

    sample_contributor = Contributor(
        login="evandro",
        url="https://github.com/evandro",
        avatar_url="https://avatars.githubusercontent.com/u/2",
        contributions=12,
        country="BR",
    )

    sample_link = Link(
        subject_kind="contract",
        subject="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        method="contract_in_repo",
        path="src/contract.rs",
    )

    sample_contract = Contract(
        contract_id="CAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        deployer="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        wasm_hash="1111111111111111111111111111111111111111111111111111111111111111",
        tx_hash="2222222222222222222222222222222222222222222222222222222222222222",
        ledger=123456,
        deployed_at=now,
        project_id="repo:stellar/wallet",
    )

    sample_wasm = WasmUpload(
        wasm_hash="1111111111111111111111111111111111111111111111111111111111111111",
        uploader="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        tx_hash="3333333333333333333333333333333333333333333333333333333333333333",
        size=40960,
        source_repo="stellar/wallet",
        full_name="stellar/wallet",
        contracts=1,
        uploaded_at=now,
    )

    sample_failed_tx = FailedTx(
        tx_hash="4444444444444444444444444444444444444444444444444444444444444444",
        source_account="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        kind="invokeHostFunction",
        result_code="txFAILED",
        ledger=123457,
        created_at=now,
    )

    sample_integration_use = IntegrationUse(
        slug="privy",
        name="Privy",
        method="package",
        evidence="@privy-io/node in package.json",
        path="package.json",
    )

    sample_project_detail = ProjectDetail(
        project=sample_project,
        links=[sample_link],
        integration_uses=[sample_integration_use],
        contributors=[sample_contributor],
        contracts=[sample_contract],
        wasm_uploads=[sample_wasm],
        failed_txs=[sample_failed_tx],
    )

    sample_builder = Builder(
        address="GAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        projects=[sample_project],
        contracts=[sample_contract],
        wasm_uploads=[sample_wasm],
        failed_txs=[sample_failed_tx],
    )

    sample_timeline = TimelinePoint(
        hour=now,
        contracts=4,
    )

    sample_integration = Integration(
        slug="privy",
        name="Privy",
        category="Auth",
        site="https://privy.io",
        projects=5,
    )

    sample_country = CountryCount(
        country="PT",
        contributors=7,
    )

    samples = {
        "stats": sample_stats,
        "project": sample_project,
        "project-detail": sample_project_detail,
        "builder": sample_builder,
        "contract": sample_contract,
        "wasm-upload": sample_wasm,
        "failed-tx": sample_failed_tx,
        "timeline-point": sample_timeline,
        "integration": sample_integration,
        "country-count": sample_country,
    }

    schemas_dir = PUBLIC / "schema"

    for slug, sample_obj in samples.items():
        schema_file = schemas_dir / f"{slug}-{API_SCHEMA_VERSION}.schema.json"
        assert schema_file.exists(), f"Missing schema file: {schema_file}"

        schema_json = json.loads(schema_file.read_text(encoding="utf-8"))

        # Verify it conforms to JSON Schema Draft 2020-12
        jsonschema.Draft202012Validator.check_schema(schema_json)

        # Validate serialized sample against the published schema
        sample_data = sample_obj.model_dump(mode="json")
        jsonschema.validate(instance=sample_data, schema=schema_json)
