import json
import logging

import yaml

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.models import SCHEMA_VERSION
from hackproof.export.render import (
    API_MODELS,
    API_SCHEMA_VERSION,
    SITE,
    api_json_schema,
    json_schema,
    to_json,
    to_yaml,
)
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

PUBLIC = ROOT / "apps" / "web" / "public"


def _write(path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def export_schemas() -> None:
    schemas = PUBLIC / "schema"
    schemas.mkdir(parents=True, exist_ok=True)

    schema = json_schema()
    _write(schemas / f"hackathon-export-{SCHEMA_VERSION}.json", json.dumps(schema, indent=2) + "\n")
    _write(
        schemas / f"hackathon-export-{SCHEMA_VERSION}.yml",
        yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=100),
    )

    index_entries = [
        {
            "name": "hackathon-export",
            "category": "export",
            "versions": ["1.0", "1.1", "1.2"],
            "latest": "1.2",
            "files": [
                "hackathon-export-1.0.json",
                "hackathon-export-1.0.yml",
                "hackathon-export-1.1.json",
                "hackathon-export-1.1.yml",
                "hackathon-export-1.2.json",
                "hackathon-export-1.2.yml",
            ],
            "url": f"{SITE}/schema/hackathon-export-{SCHEMA_VERSION}.json",
        }
    ]

    for slug, model in API_MODELS.items():
        model_schema = api_json_schema(model, slug)
        filename = f"{slug}-{API_SCHEMA_VERSION}.schema.json"
        _write(schemas / filename, json.dumps(model_schema, indent=2) + "\n")
        index_entries.append(
            {
                "name": slug,
                "category": "api",
                "model": model.__name__,
                "versions": [API_SCHEMA_VERSION],
                "latest": API_SCHEMA_VERSION,
                "files": [filename],
                "url": f"{SITE}/schema/{filename}",
            }
        )

    index_data = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SITE}/schema/index.json",
        "name": "HackProof Schema Index",
        "description": (
            "Index of all published schemas for HackProof datasets and public API models."
        ),
        "schemas": index_entries,
    }
    _write(schemas / "index.json", json.dumps(index_data, indent=2) + "\n")
    log.info("wrote %s schemas and index to %s", len(index_entries), schemas)


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    data = PUBLIC / "data" / hackathon.slug
    _write(data / "projects.json", to_json(export))
    _write(data / "projects.yml", to_yaml(export))

    export_schemas()
    log.info("wrote %s projects to %s", len(export.projects), data)
