import json
import logging

import yaml

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.render import json_schema, to_json, to_yaml
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    target = ROOT / "data" / "export" / hackathon.slug
    target.mkdir(parents=True, exist_ok=True)
    schema = json_schema()
    files = {
        "projects.json": to_json(export),
        "projects.yml": to_yaml(export),
        "schema.json": json.dumps(schema, indent=2) + "\n",
        "schema.yml": yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=100),
    }
    for name, content in files.items():
        (target / name).write_text(content)
    log.info("wrote %s projects to %s", len(export.projects), target)
