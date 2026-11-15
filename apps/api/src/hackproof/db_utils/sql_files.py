import re
from pathlib import Path

TABLE_NAME_RE = re.compile(
    r'CREATE TABLE( IF NOT EXISTS)? "?([A-Za-z_][A-Za-z0-9_]*)"?'
)


def table_name(path: Path) -> str | None:
    match = TABLE_NAME_RE.search(path.read_text())
    return match.group(2) if match else None
