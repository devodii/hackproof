from typing import Any

import yaml
from pydantic import BaseModel

from hackproof.export.models import SCHEMA_VERSION, HackathonExport
from hackproof.schemas import (
    Builder,
    Contract,
    CountryCount,
    FailedTx,
    Integration,
    Project,
    ProjectDetail,
    Stats,
    TimelinePoint,
    WasmUpload,
)

SITE = "https://hackproof.vercel.app"
SCHEMA_ID = f"{SITE}/schema/hackathon-export-{SCHEMA_VERSION}.json"
API_SCHEMA_VERSION = "1.0"

API_MODELS: dict[str, type[BaseModel]] = {
    "stats": Stats,
    "project": Project,
    "project-detail": ProjectDetail,
    "builder": Builder,
    "contract": Contract,
    "wasm-upload": WasmUpload,
    "failed-tx": FailedTx,
    "timeline-point": TimelinePoint,
    "integration": Integration,
    "country-count": CountryCount,
}


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


def api_json_schema(
    model: type[BaseModel], slug: str, version: str = API_SCHEMA_VERSION
) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SITE}/schema/{slug}-{version}.schema.json",
        **model.model_json_schema(),
    }
