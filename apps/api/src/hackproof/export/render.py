from typing import Any

import yaml

from hackproof.export.models import SCHEMA_VERSION, HackathonExport

SCHEMA_ID = f"https://hackproof.dev/schema/hackathon-export-{SCHEMA_VERSION}.json"


def to_json(export: HackathonExport) -> str:
    return export.model_dump_json(by_alias=True, indent=2) + "\n"


def to_yaml(export: HackathonExport) -> str:
    data = export.model_dump(mode="json", by_alias=True)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def json_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        **HackathonExport.model_json_schema(),
    }
