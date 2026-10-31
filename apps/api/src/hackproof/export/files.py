import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from hackproof.export.models import HackathonExport, Project, Tier, Track
from hackproof.hackathon import Place

SCHEMA_FILE = "schema-hackathon-project.yml"
SCHEMA_COMMENT = f"# yaml-language-server: $schema=../{SCHEMA_FILE}\n"


class FileModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FileEvidence(FileModel):
    kind: Literal["contract", "wasm", "account", "asset"]
    subject: str
    method: Literal[
        "contract_in_repo", "wasm_hash_match", "wasm_meta", "deployer_in_repo", "asset_in_repo"
    ]
    explorer_url: str | None = None
    file_url: str | None = None


class FileChain(FileModel):
    contracts: int
    wasm_uploads: int
    classic_ops: int
    assets: int
    failed_txs: int
    accounts: list[str]
    evidence: list[FileEvidence]


class FileIntegrationEvidence(FileModel):
    method: Literal["package", "endpoint"]
    detail: str
    file_url: str


class FileIntegration(FileModel):
    slug: str
    name: str
    evidence: list[FileIntegrationEvidence]


class FileContributor(FileModel):
    login: str
    contributions: int


class ProjectFile(FileModel):
    event: str = Field(description="Hackathon slug")
    canonical_id: str = Field(description="pkg:github/<owner>/<repo>, the join key for repos")
    repo_url: str
    name: str = Field(description="Repository name")
    description: str | None = None
    homepage: str | None = None
    language: str | None = None
    license: str | None = None
    topics: list[str] = Field(default_factory=list, description="Tags the team set on the repo")
    created_at: datetime | None = Field(default=None, description="Repo creation time, UTC")
    owner: str = Field(description="GitHub login of the repo owner")
    track: Track
    track_declared: bool = Field(
        description="True when the team states its track itself, false when track is the default"
    )
    award: Place | None = None
    evidence_tier: Tier
    commits_in_window: int | None = None
    stack: dict[str, str | None] = Field(
        default_factory=dict, description="Stellar package to declared version, null when unknown"
    )
    integrations: list[FileIntegration] = Field(default_factory=list)
    chain: FileChain
    contributors: list[FileContributor]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def file_names(projects: list[Project]) -> dict[str, str]:
    slugs = {project.repo_full_name: slugify(project.name) for project in projects}
    empty = sorted(name for name, slug in slugs.items() if not slug)
    if empty:
        raise ValueError(f"no usable file name for {', '.join(empty)}")
    counts = Counter(slugs.values())
    names = {
        name: f"{slugify(name.split('/')[0])}-{slug}" if counts[slug] > 1 else slug
        for name, slug in slugs.items()
    }
    clashes = sorted(name for name, count in Counter(names.values()).items() if count > 1)
    if clashes:
        raise ValueError(f"file names still collide: {', '.join(clashes)}")

    return names


def project_file(event: str, project: Project) -> ProjectFile:
    chain = project.chain
    return ProjectFile(
        event=event,
        canonical_id=f"pkg:github/{project.repo_full_name}",
        repo_url=project.repo_url,
        name=project.name,
        description=project.description,
        homepage=project.homepage,
        language=project.language,
        license=project.license,
        topics=project.self_tags,
        created_at=project.repo_created_at,
        owner=project.owner.login,
        track=project.track,
        track_declared=project.track_declared,
        award=project.award,
        evidence_tier=project.tier,
        commits_in_window=project.commits_in_window,
        stack=project.stack_versions,
        integrations=[
            FileIntegration(
                slug=partner.slug,
                name=partner.name,
                evidence=[
                    FileIntegrationEvidence(
                        method=item.method, detail=item.detail, file_url=item.repo_file_url
                    )
                    for item in partner.evidence
                ],
            )
            for partner in project.integration_partners
        ],
        chain=FileChain(
            contracts=chain.contract_count,
            wasm_uploads=chain.wasm_upload_count,
            classic_ops=chain.classic_op_count,
            assets=chain.asset_count,
            failed_txs=chain.failed_tx_count,
            accounts=[account.address for account in chain.accounts],
            evidence=[
                FileEvidence(
                    kind=item.kind,
                    subject=item.subject,
                    method=item.method,
                    explorer_url=item.explorer_url,
                    file_url=item.repo_file_url,
                )
                for item in chain.evidence
            ],
        ),
        contributors=[
            FileContributor(login=person.login, contributions=person.contributions)
            for person in project.contributors
        ],
    )


def to_file_yaml(file: ProjectFile) -> str:
    data = file.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120)

    return SCHEMA_COMMENT + body


def file_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **ProjectFile.model_json_schema(),
    }


def write_project_files(export: HackathonExport, root: Path) -> int:
    directory = root / str(export.hackathon.starts_at.year)
    directory.mkdir(parents=True, exist_ok=True)
    names = file_names(export.projects)
    for project in export.projects:
        path = directory / f"{names[project.repo_full_name]}.yml"
        path.write_text(to_file_yaml(project_file(export.hackathon.slug, project)))
    wanted = {f"{name}.yml" for name in names.values()}
    for stale in directory.glob("*.yml"):
        if stale.name not in wanted:
            stale.unlink()
    (root / SCHEMA_FILE).write_text(
        yaml.safe_dump(file_schema(), sort_keys=False, allow_unicode=True, width=120)
    )

    return len(export.projects)
