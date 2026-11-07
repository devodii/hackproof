import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from hackproof import schemas as api_schemas
from hackproof.export.models import HackathonExport, Project, Tier, Track
from hackproof.hackathon import Place

SCHEMA_FILE = "schema-hackathon-project.yml"
EVENT_FILE = "_event.yml"
EVENT_SCHEMA_FILE = "schema-event.yml"
SCHEMA_VERSION = "1.0"
SOURCE_URL = "https://github.com/devodii/hackproof"
SCHEMA_BASE_URL = f"{SOURCE_URL}/schema"
SCHEMA_COMMENT = f"# yaml-language-server: $schema=../{SCHEMA_FILE}\n"
EVENT_SCHEMA_COMMENT = f"# yaml-language-server: $schema=../{EVENT_SCHEMA_FILE}\n"

API_SCHEMA_MODELS: tuple[tuple[str, type[BaseModel]], ...] = (
    ("stats", api_schemas.Stats),
    ("project", api_schemas.Project),
    ("contributor", api_schemas.Contributor),
    ("link", api_schemas.Link),
    ("contract", api_schemas.Contract),
    ("wasm-upload", api_schemas.WasmUpload),
    ("failed-tx", api_schemas.FailedTx),
    ("integration-use", api_schemas.IntegrationUse),
    ("project-detail", api_schemas.ProjectDetail),
    ("builder", api_schemas.Builder),
    ("timeline-point", api_schemas.TimelinePoint),
    ("integration", api_schemas.Integration),
    ("ecosystem-tool", api_schemas.EcosystemTool),
    ("country-count", api_schemas.CountryCount),
    ("project-page", api_schemas.Page[api_schemas.Project]),
    ("contract-page", api_schemas.Page[api_schemas.Contract]),
    ("wasm-upload-page", api_schemas.Page[api_schemas.WasmUpload]),
    ("failed-tx-page", api_schemas.Page[api_schemas.FailedTx]),
)


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


class EventFile(FileModel):
    slug: str = Field(description="Event slug, lowercase words separated by hyphens")
    name: str
    network: Literal["pubnet", "testnet", "futurenet"] = Field(
        description="Stellar network the event ran on"
    )
    starts_at: datetime = Field(description="Official start, UTC")
    ends_at: datetime = Field(description="Official submission deadline, UTC")
    source_url: str | None = Field(default=None, description="Where the dataset is produced")


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
    tools: list[FileIntegration] = Field(
        default_factory=list, description="Stellar developer tools the repo builds with"
    )
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


def event_file(export: HackathonExport) -> EventFile:
    hackathon = export.hackathon
    return EventFile(
        slug=hackathon.slug,
        name=hackathon.name,
        network=hackathon.network,
        starts_at=hackathon.starts_at,
        ends_at=hackathon.submission_deadline,
        source_url=SOURCE_URL,
    )


def to_event_yaml(file: EventFile) -> str:
    data = file.model_dump(mode="json", exclude_none=True)
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120)

    return EVENT_SCHEMA_COMMENT + body


def event_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **EventFile.model_json_schema(),
    }


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
        tools=[
            FileIntegration(
                slug=tool.slug,
                name=tool.name,
                evidence=[
                    FileIntegrationEvidence(
                        method=item.method, detail=item.detail, file_url=item.repo_file_url
                    )
                    for item in tool.evidence
                ],
            )
            for tool in project.ecosystem_tools
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
    (directory / EVENT_FILE).write_text(to_event_yaml(event_file(export)))
    wanted = {f"{name}.yml" for name in names.values()} | {EVENT_FILE}
    for stale in directory.glob("*.yml"):
        if stale.name not in wanted:
            stale.unlink()
    for name, schema in ((SCHEMA_FILE, file_schema()), (EVENT_SCHEMA_FILE, event_schema())):
        (root / name).write_text(
            yaml.safe_dump(schema, sort_keys=False, allow_unicode=True, width=120)
        )

    return len(export.projects)


def api_schema(slug: str, model: type[BaseModel]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"{SCHEMA_BASE_URL}/{slug}.schema.json",
        "version": SCHEMA_VERSION,
        **model.model_json_schema(),
    }


def write_api_schemas(schema_dir: Path) -> dict[str, Any]:
    schema_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, str]] = [
        {
            "name": "hackathon-export",
            "version": SCHEMA_VERSION,
            "file": f"hackathon-export-{SCHEMA_VERSION}.json",
            "$id": f"{SCHEMA_BASE_URL}/hackathon-export-{SCHEMA_VERSION}.json",
        },
        {
            "name": "hackathon-project",
            "version": SCHEMA_VERSION,
            "file": SCHEMA_FILE,
            "$id": f"{SCHEMA_BASE_URL}/{SCHEMA_FILE}",
        },
        {
            "name": "event",
            "version": SCHEMA_VERSION,
            "file": EVENT_SCHEMA_FILE,
            "$id": f"{SCHEMA_BASE_URL}/{EVENT_SCHEMA_FILE}",
        },
    ]
    for slug, model in API_SCHEMA_MODELS:
        filename = f"{slug}.schema.json"
        schema = api_schema(slug, model)
        (schema_dir / filename).write_text(f"{json.dumps(schema, indent=2)}\n")
        entries.append(
            {
                "name": slug,
                "version": SCHEMA_VERSION,
                "file": filename,
                "$id": schema["$id"],
            }
        )
    index = {"version": SCHEMA_VERSION, "schemas": entries}
    (schema_dir / "index.json").write_text(f"{json.dumps(index, indent=2)}\n")
    return index
