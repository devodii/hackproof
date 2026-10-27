from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from hackproof.github.models import DependencyFingerprint

Tier = Literal["verified", "declared", "likely", "possible", "unattributed"]


class Stats(BaseModel):
    projects: int
    verified_projects: int
    declared_projects: int
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
    project_id: str
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
    mentions_hackathon: bool | None
    stellar_added_in_window: bool | None
    created_at: datetime | None
    topics: list[str] | None


class Contributor(BaseModel):
    login: str
    url: str
    avatar_url: str | None
    contributions: int
    country: str | None


class Link(BaseModel):
    subject_kind: str
    subject: str
    method: str
    confidence: float


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


class ProjectDetail(BaseModel):
    project: Project
    links: list[Link]
    contributors: list[Contributor]
    contracts: list[Contract]
    wasm_uploads: list[WasmUpload]
    failed_txs: list[FailedTx]


class Builder(BaseModel):
    address: str
    projects: list[Project]
    contracts: list[Contract]
    wasm_uploads: list[WasmUpload]
    failed_txs: list[FailedTx]


class ChallengeRequest(BaseModel):
    address: str


class Challenge(BaseModel):
    message: str


class ClaimRequest(BaseModel):
    address: str
    message: str
    signature: str


class Proof(BaseModel):
    proof_id: str
    address: str
    claimed_at: datetime
    projects: int
    contracts: int
    wasm_uploads: int
    failed_txs: int
    first_activity: datetime
    last_activity: datetime
    window_start: datetime
    window_end: datetime


class TimelinePoint(BaseModel):
    hour: datetime
    contracts: int


class CountryCount(BaseModel):
    country: str
    contributors: int


class Page[T](BaseModel):
    items: list[T]
    total: int
