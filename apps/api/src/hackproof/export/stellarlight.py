from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from hackproof.export.models import Project


class Model(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class StellarLightRow(Model):
    id: str = Field(description="Unique project identifier (e.g. repo:org/name)")
    event: str = Field(description="Hackathon event slug")
    name: str = Field(description="Project name")
    tagline: str | None = Field(default=None, description="Short project tagline or description")
    repo: str = Field(description="GitHub repository URL")
    repo_verified: bool = Field(description="Whether the repo has verified on-chain evidence")
    verification_evidence: list[str] = Field(
        default_factory=list,
        description="List of on-chain verification evidence items (contracts, wasms, or matches)",
    )
    builders: list[str] = Field(
        default_factory=list, description="List of contributor GitHub logins"
    )
    official_status: str = Field(
        description="Official event status: first, runner-up, or submitted"
    )


def map_project_to_stellarlight(project: Project, event_slug: str) -> StellarLightRow:
    """Map a HackProof Project model to a Stellar Light hackathon submission row."""
    evidence_items: list[str] = []
    if project.chain:
        for ev in project.chain.evidence:
            evidence_items.append(f"{ev.kind}:{ev.subject}")
        for c in project.chain.contracts:
            if c.contract_id not in evidence_items:
                evidence_items.append(c.contract_id)

    builders = [c.login for c in project.contributors]
    status = project.award if project.award is not None else "submitted"
    project_id = f"repo:{project.repo_full_name}"

    return StellarLightRow(
        id=project_id,
        event=event_slug,
        name=project.name,
        tagline=project.description,
        repo=project.repo_url,
        repo_verified=(project.tier == "verified"),
        verification_evidence=evidence_items,
        builders=builders,
        official_status=status,
    )


def export_stellarlight(projects: list[Project], event_slug: str) -> list[dict[str, Any]]:
    """Export a list of projects into a list of Stellar Light submission dictionaries."""
    rows = [map_project_to_stellarlight(p, event_slug) for p in projects]
    return [row.model_dump(mode="json", by_alias=True) for row in rows]


def stellarlight_json_schema() -> dict[str, Any]:
    """Return JSON Schema for the Stellar Light dataset."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://hackproof.vercel.app/schema/stellarlight.json",
        "title": "StellarLightSubmissions",
        "type": "array",
        "items": StellarLightRow.model_json_schema(),
    }
