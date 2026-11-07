import csv
import re
import xml.etree.ElementTree as ET
import zipfile

from hackproof.config import ROOT
from hackproof.export.judges import JUDGE_COLUMNS, write_judge_files
from tests.test_export import populated_export


def documented_columns() -> list[str]:
    doc = (ROOT / "docs" / "judge-export.md").read_text(encoding="utf-8")
    return re.findall(r"^\| `([a-z_]+)` \|", doc, flags=re.MULTILINE)


async def test_judge_export_headers_match_documented_columns_and_open_cleanly(
    scratch_db, tmp_path
):
    export = await populated_export(scratch_db)
    csv_path, xlsx_path = write_judge_files(export, tmp_path)

    expected = documented_columns()
    assert list(JUDGE_COLUMNS) == expected

    with csv_path.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == expected
    assert len(rows) == 2
    assert rows[1][0] == "https://github.com/team/app"
    assert rows[1][1] == "verified"

    with zipfile.ZipFile(xlsx_path) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml")
    root = ET.fromstring(sheet_xml)
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    first_row = root.find(".//s:row[@r='1']", ns)
    assert first_row is not None
    xlsx_headers = [t.text for t in first_row.findall(".//s:t", ns)]
    assert xlsx_headers == expected
