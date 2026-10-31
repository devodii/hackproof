import csv
import re
from datetime import UTC, datetime
from pathlib import Path

import openpyxl

from hackproof.export.judges import (
    COLUMNS,
    build_judge_row,
    export_judges_csv,
    export_judges_xlsx,
)
from hackproof.export.models import (
    Chain,
    Contract,
    Contributor,
    Owner,
    Project,
)


def _sample_project() -> Project:
    now = datetime(2026, 10, 25, 14, 30, tzinfo=UTC)
    return Project(
        repo_full_name="org/judge-test",
        name="judge-test",
        repo_url="https://github.com/org/judge-test",
        description="Judge evaluation test repo",
        homepage="https://demo.judge-test.com",
        tier="verified",
        track="genesis",
        award="first",
        language="Rust",
        license="MIT",
        stars=10,
        forks=2,
        self_tags=["stellar"],
        stack=["soroban-sdk"],
        stack_versions={"soroban-sdk": "22.0.0"},
        repo_created_at=now,
        repo_last_commit_at=now,
        commits_in_window=8,
        total_commits=12,
        integration_partners=[],
        owner=Owner(login="org", avatar_url=None, country="US"),
        contributors=[
            Contributor(
                login="dev1",
                url="https://github.com/dev1",
                avatar_url=None,
                contributions=5,
                country="US",
            )
        ],
        chain=Chain(
            contract_count=2,
            wasm_upload_count=1,
            classic_op_count=0,
            asset_count=0,
            failed_tx_count=1,
            accounts=[],
            wasm_uploads=[],
            contracts=[
                Contract(
                    contract_id="C111111111111111111111111111111111111111111111111111111111111111",
                    deployer="G111111111111111111111111111111111111111111111111111111111111111",
                    wasm_hash="hash1",
                    deployed_at=now,
                    ledger=100,
                    tx_hash="tx1",
                    explorer_url="https://stellar.expert/contract/C1",
                    tx_url="https://stellar.expert/tx/tx1",
                )
            ],
            evidence=[],
        ),
    )


def test_header_row_matches_documented_columns():
    # Read documented columns from docs/judge-export.md
    docs_path = Path(__file__).resolve().parents[3] / "docs" / "judge-export.md"
    assert docs_path.exists(), f"docs/judge-export.md must exist at {docs_path}"

    content = docs_path.read_text(encoding="utf-8")
    # Extract backtick column names from markdown table
    documented_columns = re.findall(r"\|\s*`([a-z0-9_]+)`\s*\|", content)

    # Acceptance criteria: A test checks the header row against the documented columns
    assert len(documented_columns) > 0, "No documented columns found in docs/judge-export.md"
    assert documented_columns == COLUMNS, "Code COLUMNS must exactly match docs/judge-export.md"


def test_export_judges_csv_and_xlsx(tmp_path: Path):
    project = _sample_project()
    csv_file = tmp_path / "judges.csv"
    xlsx_file = tmp_path / "judges.xlsx"

    export_judges_csv([project], csv_file)
    export_judges_xlsx([project], xlsx_file)

    # Verify CSV opens cleanly
    assert csv_file.exists()
    with csv_file.open("r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        headers = reader[0]
        assert headers == COLUMNS
        assert len(reader) == 2
        row = dict(zip(headers, reader[1], strict=True))
        assert row["repo_url"] == "https://github.com/org/judge-test"
        assert row["evidence_tier"] == "verified"
        assert row["contracts"] == "2"
        assert row["deploys"] == "1"
        assert row["has_demo_url"] == "True"
        assert row["failed_transactions"] == "1"
        assert row["first_deploy_time"] == "2026-10-25T14:30:00Z"

    # Verify XLSX opens cleanly with openpyxl
    assert xlsx_file.exists()
    wb = openpyxl.load_workbook(xlsx_file)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    xlsx_headers = list(rows[0])
    assert xlsx_headers == COLUMNS
    assert len(rows) == 2
    xlsx_row = dict(zip(xlsx_headers, rows[1], strict=True))
    assert xlsx_row["repo_url"] == "https://github.com/org/judge-test"
    assert xlsx_row["contracts"] == 2
    assert xlsx_row["has_demo_url"] is True


def test_build_judge_row_no_subjective_scores():
    project = _sample_project()
    row = build_judge_row(project)
    for col in row:
        assert "score" not in col.lower()
        assert "rank" not in col.lower()
        assert "points" not in col.lower()
