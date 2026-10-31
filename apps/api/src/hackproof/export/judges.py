import csv
import logging
from datetime import UTC
from pathlib import Path
from typing import Any

import openpyxl

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.models import Project
from hackproof.hackathon import get_hackathon

log = logging.getLogger(__name__)

PUBLIC = ROOT / "apps" / "web" / "public"

# Documented objective columns in docs/judge-export.md
COLUMNS: list[str] = [
    "repo_url",
    "evidence_tier",
    "contracts",
    "deploys",
    "first_deploy_time",
    "invocations",
    "failed_transactions",
    "has_tests",
    "test_file_count",
    "has_ci",
    "readme_length",
    "readme_sections",
    "has_demo_url",
    "has_video_url",
    "ai_attribution_present",
    "mainnet_status",
]


def build_judge_row(project: Project) -> dict[str, Any]:
    """Map a Project model into an objective evaluation row for judges."""
    first_deploy = ""
    contracts_count = 0
    deploys_count = 0
    failed_txs = 0

    if project.chain:
        contracts_count = project.chain.contract_count
        deploys_count = len(project.chain.contracts)
        failed_txs = project.chain.failed_tx_count
        if project.chain.contracts:
            earliest_dt = min(c.deployed_at for c in project.chain.contracts)
            utc_dt = earliest_dt.astimezone(UTC)
            first_deploy = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    has_demo = False
    if project.homepage and ("http://" in project.homepage or "https://" in project.homepage):
        has_demo = True

    return {
        "repo_url": project.repo_url,
        "evidence_tier": project.tier,
        "contracts": contracts_count,
        "deploys": deploys_count,
        "first_deploy_time": first_deploy,
        "invocations": "",
        "failed_transactions": failed_txs,
        "has_tests": "",
        "test_file_count": "",
        "has_ci": "",
        "readme_length": "",
        "readme_sections": "",
        "has_demo_url": has_demo,
        "has_video_url": "",
        "ai_attribution_present": "",
        "mainnet_status": "",
    }


def export_judges_csv(projects: list[Project], output_path: Path) -> Path:
    """Write projects to CSV with documented columns."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for p in projects:
            row_dict = build_judge_row(p)
            writer.writerow([row_dict.get(col, "") for col in COLUMNS])

    return output_path


def export_judges_xlsx(projects: list[Project], output_path: Path) -> Path:
    """Write projects to XLSX with documented columns."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Judges"
    ws.append(COLUMNS)
    for p in projects:
        row_dict = build_judge_row(p)
        ws.append([row_dict.get(col, "") for col in COLUMNS])

    wb.save(output_path)
    return output_path


async def run_export_judges(
    csv_path: Path | None = None,
    xlsx_path: Path | None = None,
) -> tuple[Path, Path]:
    """Execute judges export generating both CSV and XLSX files."""
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    data_dir = PUBLIC / "data" / hackathon.slug
    if csv_path is None:
        csv_path = data_dir / "judges.csv"
    if xlsx_path is None:
        xlsx_path = data_dir / "judges.xlsx"

    export_judges_csv(export.projects, csv_path)
    export_judges_xlsx(export.projects, xlsx_path)

    log.info("Exported %s judge rows to %s and %s", len(export.projects), csv_path, xlsx_path)
    print(f"Exported {len(export.projects)} rows to:\n  {csv_path}\n  {xlsx_path}")
    return csv_path, xlsx_path
