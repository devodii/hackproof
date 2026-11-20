from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from hackproof.github.models import DependencyFingerprint
from hackproof.hackathon import Place
from hackproof.integrations.models import Method
from hackproof.integrations.profile import IntegrationProfile

Tier = Literal["verified", "likely", "possible", "unattributed"]


HackathonStatus = Literal["upcoming", "live", "past"]


class HackathonSummary(BaseModel):
    slug: str
    name: str
    summary: str | None
    website: str | None
    location: str | None
    starts_at: datetime
    ends_at: datetime
    status: HackathonStatus
    indexed: bool
    projects: int
    verified_projects: int
    contracts: int
    winners: int


class Stats(BaseModel):
    projects: int
    verified_projects: int
    likely_projects: int
    possible_projects: int
    unattributed_accounts: int
    contracts: int
    builders: int
    contributors: int
    countries: int
    wasm_uploads: int
    failed_txs: int


class Project(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    project_id: str
    hackathon: str
    full_name: str | None
    url: str | None
    footprint: Literal["contracts", "classic", "github"]
    tier: Tier
    contracts: int
    classic_ops: int
    assets: int
    builders: int
    wasm_uploads: int
    failed_txs: int
    first_activity: datetime | None
    last_activity: datetime | None
    description: str | None
    homepage: str | None
    stars: int | None
    forks: int | None
    language: str | None
    license: str | None
    owner: str | None
    owner_avatar: str | None
    country: str | None
    dependencies: DependencyFingerprint | None
    window_commits: int | None
    total_commits: int | None
    stellar_added_in_window: bool | None
    created_at: datetime | None
    topics: list[str] | None
    track: Literal["genesis", "scale"] | None = None
    integrations: list[str] = []
    tools: list[str] = []
    agents: list[str] = []
    award: Place | None = None


class Contributor(BaseModel):
    login: str
    url: str
    avatar_url: str | None
    contributions: int
    country: str | None


class PersonProject(BaseModel):
    project: Project
    contributions: int


class Person(BaseModel):
    login: str
    url: str
    avatar_url: str | None
    country: str | None
    contributions: int
    projects: list[PersonProject]


class Link(BaseModel):
    subject_kind: str
    subject: str
    method: str
    path: str | None


class Contract(BaseModel):
    contract_id: str
    deployer: str
    wasm_hash: str
    tx_hash: str
    ledger: int
    deployed_at: datetime
    project_id: str


class WasmUpload(BaseModel):
    wasm_hash: str
    uploader: str
    tx_hash: str
    size: int
    source_repo: str | None
    full_name: str | None
    contracts: int
    uploaded_at: datetime


class FailedTx(BaseModel):
    tx_hash: str
    source_account: str
    kind: str
    result_code: str
    ledger: int
    created_at: datetime


class IntegrationUse(BaseModel):
    slug: str
    name: str
    method: Method
    evidence: str
    path: str


class IntegrationDepth(BaseModel):
    slug: str
    name: str
    profile: IntegrationProfile


class ProjectDetail(BaseModel):
    project: Project
    links: list[Link]
    integration_uses: list[IntegrationUse]
    integration_depths: list[IntegrationDepth]
    tool_uses: list[IntegrationUse]
    contributors: list[Contributor]
    contracts: list[Contract]
    wasm_uploads: list[WasmUpload]
    failed_txs: list[FailedTx]


class Account(BaseModel):
    address: str
    projects: list[Project]
    contracts: list[Contract]
    wasm_uploads: list[WasmUpload]
    failed_txs: list[FailedTx]


class TimelinePoint(BaseModel):
    hour: datetime
    contracts: int


class Integration(BaseModel):
    slug: str
    name: str
    category: str
    site: str
    projects: int
    deep: bool


class EcosystemTool(BaseModel):
    slug: str
    name: str
    site: str
    projects: int
    deep: bool


class AIAgent(BaseModel):
    slug: str
    name: str
    site: str
    projects: int


class CountryCount(BaseModel):
    country: str
    contributors: int


class Count(BaseModel):
    label: str
    value: int


class WrappedBuilder(BaseModel):
    login: str
    avatar_url: str | None
    projects: int
    contributions: int
    project_names: list[str]


class Wrapped(BaseModel):
    builders: int
    accounts_funded: int
    deployers: int
    operations: int
    largest_wasm_contracts: int
    operations_by_type: list[Count]
    team_sizes: list[Count]
    multi_team_builders: list[WrappedBuilder]
    top_builders: list[WrappedBuilder]


class Page[T](BaseModel):
    items: list[T]
    total: int
