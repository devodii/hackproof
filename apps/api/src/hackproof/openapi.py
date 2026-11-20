import json
from pathlib import Path

from hackproof.config import ROOT
from hackproof.main import app

SCHEMA_FILE = ROOT / "apps" / "web" / "openapi.json"


def render() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def write(path: Path = SCHEMA_FILE) -> None:
    path.write_text(render())
