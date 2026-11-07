import csv
import logging
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import STRICT_TIERS, build_export
from hackproof.export.models import HackathonExport, Project
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export.judges")

JUDGE_COLUMNS: tuple[str, ...] = (
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
)

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml"
    ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml"
    ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="xl/workbook.xml"/>
</Relationships>
"""

WORKBOOK_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Submissions" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
"""

WORKBOOK_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
    Target="worksheets/sheet1.xml"/>
</Relationships>
"""


def _col_letter(index: int) -> str:
    letters = ""
    current = index + 1
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _project_row(project: Project) -> dict[str, str | int]:
    deploys = project.chain.contracts
    first_deploy = (
        min(c.deployed_at for c in deploys).strftime("%Y-%m-%dT%H:%M:%SZ") if deploys else ""
    )
    return {
        "repo_url": project.repo_url,
        "evidence_tier": project.tier,
        "contracts": project.chain.contract_count,
        "deploys": len(deploys),
        "first_deploy_time": first_deploy,
        "invocations": "",
        "failed_transactions": project.chain.failed_tx_count,
        "has_tests": "",
        "test_file_count": "",
        "has_ci": "",
        "readme_length": "",
        "readme_sections": "",
        "has_demo_url": "true" if project.homepage else "false",
        "has_video_url": "",
        "ai_attribution_present": "",
        "mainnet_status": "",
    }


def _sheet_xml(rows: list[list[str | int]]) -> str:
    xml_rows: list[str] = []
    for r_idx, row in enumerate(rows, start=1):
        cells: list[str] = []
        for c_idx, value in enumerate(row):
            ref = f"{_col_letter(c_idx)}{r_idx}"
            if isinstance(value, int):
                cells.append(f'<c r="{ref}" t="n"><v>{value}</v></c>')
            else:
                escaped = escape(str(value))
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escaped}</t></is></c>')
        xml_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    body = "".join(xml_rows)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{body}</sheetData>"
        "</worksheet>"
    )


def write_judge_files(export: HackathonExport, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "judges.csv"
    xlsx_path = output_dir / "judges.xlsx"

    dict_rows = [_project_row(project) for project in export.projects]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(JUDGE_COLUMNS))
        writer.writeheader()
        writer.writerows(dict_rows)

    matrix: list[list[str | int]] = [list(JUDGE_COLUMNS)]
    for row in dict_rows:
        matrix.append([row[col] for col in JUDGE_COLUMNS])

    with zipfile.ZipFile(xlsx_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        archive.writestr("_rels/.rels", RELS_XML)
        archive.writestr("xl/workbook.xml", WORKBOOK_XML)
        archive.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS_XML)
        archive.writestr("xl/worksheets/sheet1.xml", _sheet_xml(matrix))

    return csv_path, xlsx_path


async def run_export_judges(output_dir: Path | None = None) -> tuple[Path, Path]:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon, STRICT_TIERS)
    target = output_dir or (ROOT / "data" / str(export.hackathon.starts_at.year))
    csv_path, xlsx_path = write_judge_files(export, target)
    log.info("wrote judge exports to %s and %s", csv_path, xlsx_path)
    return csv_path, xlsx_path
