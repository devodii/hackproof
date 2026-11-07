import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from hackproof.export.models import Evidence, HackathonExport, Project


class StellarLightRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    event: str
    name: str
    tagline: str | None
    repo: str
    repo_verified: bool
    verification_evidence: list[Evidence]
    builders: list[str]
    official_status: Literal["first", "runner-up", "submitted"]


def to_stellarlight_row(event: str, project: Project) -> StellarLightRow:
    status: Literal["first", "runner-up", "submitted"] = (
        project.award if project.award is not None else "submitted"
    )
    return StellarLightRow(
        id=f"pkg:github/{project.repo_full_name}",
        event=event,
        name=project.name,
        tagline=project.description,
        repo=project.repo_url,
        repo_verified=project.tier == "verified",
        verification_evidence=project.chain.evidence,
        builders=[c.login for c in project.contributors],
        official_status=status,
    )


def stellarlight_rows(export: HackathonExport) -> list[StellarLightRow]:
    return [to_stellarlight_row(export.hackathon.slug, p) for p in export.projects]


def stellarlight_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/devodii/hackproof/schema/stellarlight.schema.json",
        **StellarLightRow.model_json_schema(),
    }


def write_stellarlight(
    export: HackathonExport,
    data_dir: Path,
    schema_dir: Path | None = None,
    diff: bool = False,
) -> list[dict[str, Any]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    rows = [r.model_dump(mode="json") for r in stellarlight_rows(export)]
    out_path = data_dir / "stellarlight.json"

    if diff and out_path.exists():
        previous = {item["id"]: item for item in json.loads(out_path.read_text())}
        current = {item["id"]: item for item in rows}
        added = sorted(set(current) - set(previous))
        removed = sorted(set(previous) - set(current))
        changed = sorted(k for k in set(current) & set(previous) if current[k] != previous[k])
        print(f"stellarlight diff: +{len(added)} -{len(removed)} ~{len(changed)}")

    out_path.write_text(f"{json.dumps(rows, indent=2)}\n")
    target_schema_dir = schema_dir or data_dir
    target_schema_dir.mkdir(parents=True, exist_ok=True)
    (target_schema_dir / "stellarlight.schema.json").write_text(
        f"{json.dumps(stellarlight_schema(), indent=2)}\n"
    )
    return rows
