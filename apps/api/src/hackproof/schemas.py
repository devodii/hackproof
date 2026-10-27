from datetime import datetime

from pydantic import BaseModel


class Stats(BaseModel):
    projects: int
    linked_projects: int
    contracts: int
    builders: int
    countries: int
    wasm_uploads: int
    failed_txs: int


class Project(BaseModel):
    project_id: str
    full_name: str | None
    contracts: int
    builders: int
    wasm_uploads: int
    failed_txs: int
    first_deployed_at: datetime
    last_deployed_at: datetime
    description: str | None
    stars: int | None
    owner: str | None
    owner_avatar: str | None
    country: str | None


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


class Page[T](BaseModel):
    items: list[T]
    total: int
