from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from hackproof.export.models import Project


class Model(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AtlasRow(Model):
    repo: str = Field(description="Repository URL")
    project: str = Field(description="Project name")
    program: str = Field(description="Program or hackathon identifier")
    person_or_org: str = Field(description="GitHub login of the owner or organization")
    language: str | None = Field(default=None, description="Primary programming language")
    chain_evidence: list[str] = Field(
        default_factory=list,
        description="On-chain evidence items such as deployed contracts or uploaded wasms",
    )


def map_project_to_atlas(project: Project, program_name: str) -> AtlasRow:
    """Map a HackProof Project model to an ATLAS ecosystem row."""
    chain_items: list[str] = []
    if project.chain:
        for c in project.chain.contracts:
            if c.contract_id not in chain_items:
                chain_items.append(c.contract_id)
        for w in project.chain.wasm_uploads:
            if w.wasm_hash not in chain_items:
                chain_items.append(w.wasm_hash)

    return AtlasRow(
        repo=project.repo_url,
        project=project.name,
        program=program_name,
        person_or_org=project.owner.login,
        language=project.language,
        chain_evidence=chain_items,
    )


def export_atlas(projects: list[Project], program_name: str) -> list[dict[str, Any]]:
    """Export a list of projects into a list of ATLAS rows."""
    rows = [map_project_to_atlas(p, program_name) for p in projects]
    return [row.model_dump(mode="json", by_alias=True) for row in rows]


def atlas_json_schema() -> dict[str, Any]:
    """Return JSON Schema for the ATLAS dataset."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://hackproof.vercel.app/schema/atlas.json",
        "title": "AtlasSubmissions",
        "type": "array",
        "items": AtlasRow.model_json_schema(),
    }
