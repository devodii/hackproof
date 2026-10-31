import json
import logging
from pathlib import Path
from typing import Any

import yaml

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.atlas import atlas_json_schema, export_atlas
from hackproof.export.build import build_export
from hackproof.export.diff import compute_diff
from hackproof.export.models import SCHEMA_VERSION
from hackproof.export.render import json_schema, to_json, to_yaml
from hackproof.export.stellarlight import export_stellarlight, stellarlight_json_schema
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

PUBLIC = ROOT / "apps" / "web" / "public"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read_json(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception as e:
        log.warning("Could not parse existing export at %s: %s", path, e)
    return None


async def run_export(target: str = "all", diff: bool = False) -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    data_dir = PUBLIC / "data" / hackathon.slug
    schemas_dir = PUBLIC / "schema"

    # Target: hackproof / default
    if target in ("all", "hackproof"):
        _write(data_dir / "projects.json", to_json(export))
        _write(data_dir / "projects.yml", to_yaml(export))

        schema = json_schema()
        _write(
            schemas_dir / f"hackathon-export-{SCHEMA_VERSION}.json",
            json.dumps(schema, indent=2) + "\n",
        )
        _write(
            schemas_dir / f"hackathon-export-{SCHEMA_VERSION}.yml",
            yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=100),
        )
        log.info("wrote %s projects to %s", len(export.projects), data_dir)

    # Target: stellarlight
    if target in ("all", "stellarlight"):
        sl_data = export_stellarlight(export.projects, hackathon.slug)
        sl_file = data_dir / "stellarlight.json"
        if diff:
            existing_sl = _read_json(sl_file)
            compute_diff(existing_sl, sl_data, key_field="id", target_name="StellarLight")

        _write(sl_file, json.dumps(sl_data, indent=2) + "\n")
        _write(
            schemas_dir / "stellarlight.json",
            json.dumps(stellarlight_json_schema(), indent=2) + "\n",
        )
        log.info("wrote %s StellarLight submissions to %s", len(sl_data), sl_file)

    # Target: atlas
    if target in ("all", "atlas"):
        atlas_data = export_atlas(export.projects, hackathon.name)
        atlas_file = data_dir / "atlas.json"
        if diff:
            existing_atlas = _read_json(atlas_file)
            compute_diff(existing_atlas, atlas_data, key_field="repo", target_name="ATLAS")

        _write(atlas_file, json.dumps(atlas_data, indent=2) + "\n")
        _write(
            schemas_dir / "atlas.json",
            json.dumps(atlas_json_schema(), indent=2) + "\n",
        )
        log.info("wrote %s ATLAS rows to %s", len(atlas_data), atlas_file)
