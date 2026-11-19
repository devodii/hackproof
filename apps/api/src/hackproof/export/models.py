from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hackproof.hackathon import Place
from hackproof.integrations.models import Method
from hackproof.integrations.profile import IntegrationProfile

Tier = Literal["verified", "likely", "possible"]
Track = Literal["genesis", "scale"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Owner(Model):
    login: str = Field(description="GitHub login of the repo owner")
    avatar_url: str | None = Field(description="Avatar image url")
    country: str | None = Field(
        description="ISO 3166-1 alpha-2 country derived from the owner's public GitHub location"
    )


class Contributor(Model):
    login: str = Field(description="GitHub login")
    url: str = Field(description="GitHub profile url")
    avatar_url: str | None = Field(description="Avatar image url")
    contributions: int = Field(
        description="Commits to the default branch, as GitHub counts them"
    )
    country: str | None = Field(
        description="ISO 3166-1 alpha-2 country derived from the public GitHub location"
    )


class Account(Model):
    address: str = Field(description="Stellar account (G...)")
    explorer_url: str = Field(
        description="Stellar Expert page for the account on testnet"
    )


class WasmUpload(Model):
    wasm_hash: str = Field(description="sha256 of the contract wasm, hex")
    upload_tx: str = Field(description="Hash of the transaction that uploaded the wasm")
    explorer_url: str = Field(
        description="Stellar Expert page for the upload transaction"
    )


class Contract(Model):
    contract_id: str = Field(description="Soroban contract id (C...)")
    deployer: str = Field(
        description="Stellar account (G...) that deployed the contract"
    )
    wasm_hash: str = Field(description="sha256 of the contract wasm, hex")
    deployed_at: datetime = Field(description="Ledger close time of the deploy, UTC")
    ledger: int = Field(description="Ledger sequence of the deploy")
    tx_hash: str = Field(description="Hash of the deploy transaction")
    explorer_url: str = Field(
        description="Stellar Expert page for the contract on testnet"
    )
    tx_url: str = Field(description="Stellar Expert page for the deploy transaction")


class Evidence(Model):
    kind: Literal["contract", "wasm", "account", "asset"] = Field(
        description="What was matched between the repo and the chain"
    )
    subject: str = Field(
        description="The matched contract id, wasm hash, account or CODE:ISSUER"
    )
    method: Literal[
        "contract_in_repo",
        "wasm_hash_match",
        "wasm_meta",
        "deployer_in_repo",
        "asset_in_repo",
    ] = Field(
        description="How the match was made; every method is an exact string match"
    )
    explorer_url: str | None = Field(
        description="Stellar Expert page for the matched item; null for a wasm hash"
    )
    repo_file_url: str | None = Field(
        description="GitHub file where the match was found; null when the evidence is not in a file"
    )


class Chain(Model):
    contract_count: int = Field(
        description="Contracts deployed inside the official window"
    )
    wasm_upload_count: int = Field(
        description="Distinct wasm uploads inside the window"
    )
    classic_op_count: int = Field(
        description="Classic operations by the project's accounts"
    )
    asset_count: int = Field(
        description="Assets issued inside the window by the project's accounts"
    )
    failed_tx_count: int = Field(
        description="Failed Soroban transactions by the project's accounts"
    )
    accounts: list[Account] = Field(
        description="Stellar accounts attributed to the project"
    )
    wasm_uploads: list[WasmUpload] = Field(
        description="Wasm uploaded by the project's accounts"
    )
    contracts: list[Contract] = Field(
        description="Contracts deployed inside the window"
    )
    evidence: list[Evidence] = Field(
        description="Direct repo-to-chain matches behind the tier"
    )


class IntegrationEvidence(Model):
    method: Method = Field(
        description=(
            "How the integration was found. package: declared in a dependency manifest. "
            "endpoint: the partner's API host appears in source or config, which covers raw "
            "API use without an SDK. contract: one of the partner's known contract ids appears "
            "in the repo. signal: a usage pattern from the partner's profile matched in source. "
            "capture: a value pulled out of source, written as name:value. A mention in prose "
            "never counts, except a contract id."
        )
    )
    detail: str = Field(
        description="The matched package name, API host, contract id, signal id or name:value"
    )
    repo_file_url: str = Field(description="GitHub file where it was found")


class AgentEvidence(Model):
    method: Literal["file", "author"] = Field(
        description=(
            "How the agent was found. file: one of its config files is in the repo. author: it "
            "appears as a commit author. Using a tool that leaves no trace is not counted."
        )
    )
    detail: str = Field(description="The matched file pattern or commit author login")
    repo_file_url: str | None = Field(
        description="GitHub file where it was found; null for a commit author"
    )


class AiAgent(Model):
    slug: str = Field(description="Stable agent id, listed in data/integrations.yaml")
    name: str = Field(description="Agent name")
    website: str = Field(description="Agent website")
    evidence: list[AgentEvidence] = Field(description="Where the agent was found")


class EcosystemTool(Model):
    slug: str = Field(description="Stable tool id, listed in data/integrations.yaml")
    name: str = Field(description="Tool name")
    website: str = Field(description="Tool website")
    evidence: list[IntegrationEvidence] = Field(description="Where the tool was found")


class IntegrationPartner(Model):
    slug: str = Field(description="Stable partner id, listed in data/integrations.yaml")
    name: str = Field(description="Partner name")
    category: str = Field(description="payments, wallets, defi or cross-chain")
    website: str = Field(description="Partner website")
    evidence: list[IntegrationEvidence] = Field(
        description="Where the integration was found"
    )
    profile: IntegrationProfile | None = Field(
        default=None,
        description="How deeply the repo integrates the partner, for partners with a profile in data/integrations.yaml",
    )


class Project(Model):
    repo_full_name: str = Field(
        description="GitHub owner/name; the stable key for a project"
    )
    repo_url: str = Field(description="GitHub url")
    name: str = Field(description="Repository name")
    description: str | None = Field(description="GitHub repo description")
    homepage: str | None = Field(description="Homepage or demo url set on the repo")
    tier: Tier = Field(
        description=(
            "Evidence strength. verified: exact repo-to-chain match with activity in the window. "
            "likely: Stellar dependency and at least 5 commits in the window, created or Stellar "
            "added in the window. possible: Stellar dependency and at least 3 commits in the "
            "window only."
        )
    )
    track: Track = Field(
        description=(
            "HackMeridian track the team declares in its repo docs. genesis: a new idea or early "
            "prototype. scale: an existing product or advanced prototype. Repos that do not "
            "declare one are listed as genesis."
        )
    )
    track_declared: bool = Field(
        description="True when the team states its track itself, false when track is the default"
    )
    award: Place | None = Field(
        description="HackMeridian award as announced by Build on Stellar: first, runner-up or null"
    )
    language: str | None = Field(description="Primary language")
    license: str | None = Field(description="SPDX license id")
    stars: int = Field(description="Stargazers")
    forks: int = Field(description="Forks")
    self_tags: list[str] = Field(description="GitHub topics set by the team")
    stack: list[str] = Field(
        description="Stellar packages the repo's manifests declare"
    )
    stack_versions: dict[str, str | None] = Field(
        description="Declared version for each stack package, as written in the manifest"
    )
    repo_created_at: datetime | None = Field(description="Repo creation time, UTC")
    repo_last_commit_at: datetime | None = Field(
        description="Last push to the repo, UTC"
    )
    commits_in_window: int | None = Field(
        description="Commits inside the official window"
    )
    total_commits: int | None = Field(description="Commits on the default branch")
    integration_partners: list[IntegrationPartner] = Field(
        description="Stellar ecosystem partners the repo integrates, from the SCF integration list"
    )
    ecosystem_tools: list[EcosystemTool] = Field(
        description="Stellar developer tools the repo builds with, such as Scaffold Stellar"
    )
    ai_agents: list[AiAgent] = Field(
        description="AI coding agents the repo shows traces of, such as Claude Code or Cursor"
    )
    owner: Owner
    contributors: list[Contributor]
    chain: Chain


class Hackathon(Model):
    slug: str = Field(description="Stable identifier")
    name: str
    network: Literal["testnet"]
    starts_at: datetime = Field(description="Official start, UTC")
    submission_deadline: datetime = Field(
        description="Official submission deadline, UTC"
    )


class HackathonExport(Model):
    hackathon: Hackathon
    projects: list[Project]
