import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from hackproof.export.models import Evidence, HackathonExport, Project


class AtlasRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo: str
    project: str
    program: str
    person_or_org: str
    language: str | None
    chain_evidence: list[Evidence]


def to_atlas_row(program: str, project: Project) -> AtlasRow:
    return AtlasRow(
        repo=project.repo_url,
        project=project.name,
        program=program,
        person_or_org=project.owner.login,
        language=project.language,
        chain_evidence=project.chain.evidence,
    )


def atlas_rows(export: HackathonExport) -> list[AtlasRow]:
    return [to_atlas_row(export.hackathon.slug, p) for p in export.projects]


def atlas_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/devodii/hackproof/schema/atlas.schema.json",
        **AtlasRow.model_json_schema(),
    }


def write_atlas(
    export: HackathonExport,
    data_dir: Path,
    schema_dir: Path | None = None,
    diff: bool = False,
) -> list[dict[str, Any]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    rows = [r.model_dump(mode="json") for r in atlas_rows(export)]
    out_path = data_dir / "atlas.json"

    if diff and out_path.exists():
        previous = {item["repo"]: item for item in json.loads(out_path.read_text())}
        current = {item["repo"]: item for item in rows}
        added = sorted(set(current) - set(previous))
        removed = sorted(set(previous) - set(current))
        changed = sorted(k for k in set(current) & set(previous) if current[k] != previous[k])
        print(f"atlas diff: +{len(added)} -{len(removed)} ~{len(changed)}")

    out_path.write_text(f"{json.dumps(rows, indent=2)}\n")
    target_schema_dir = schema_dir or data_dir
    target_schema_dir.mkdir(parents=True, exist_ok=True)
    (target_schema_dir / "atlas.schema.json").write_text(
        f"{json.dumps(atlas_schema(), indent=2)}\n"
    )
    return rows
