import hashlib
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field
from stellar_sdk import xdr

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot

METHODS = {"get", "post", "put", "patch", "delete"}
FAULT_WORDS = ("required", "must", "invalid", "not supported", "incomplete")
INTERNAL_PREFIXES = ("/admin", "/auth")
ESCROW_FUNCTIONS = (
    "tw_new_single_release_escrow",
    "tw_new_multi_release_escrow",
    "approve_milestone",
    "approve_milestones",
    "approve_and_release_milestones",
    "manage_milestones",
    "release_funds",
    "release_milestone_funds",
    "dispute_escrow",
    "dispute_milestone",
    "dispute_milestones",
    "resolve_dispute",
    "withdraw_remaining_funds",
    "extend_contract_ttl",
)


class Operation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    summary: str | None = None
    description: str | None = None
    responses: dict[str, Any] = Field(default_factory=dict)


class Info(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: str = ""


class Schema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    info: Info = Field(default_factory=Info)
    paths: dict[str, dict[str, Any]] = Field(default_factory=dict)


class Release(BaseModel):
    model_config = ConfigDict(extra="ignore")

    versions: dict[str, Any] = Field(default_factory=dict)
    time: dict[str, str] = Field(default_factory=dict)
    dist_tags: dict[str, str] = Field(default_factory=dict, alias="dist-tags")


class Repository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    open_issues_count: int = 0
    stargazers_count: int = 0
    forks_count: int = 0
    pushed_at: str = ""
    archived: bool = False


async def observe_api(
    http: httpx.AsyncClient, contract: ProfileContract
) -> ContractSnapshot | None:
    started = time.monotonic()
    schema_path = contract.attributes.get("schema", "docs-json")
    response = await http.get(f"{contract.id}/{schema_path}")
    if response.status_code != 200:
        return None
    latency = int((time.monotonic() - started) * 1000)
    schema = Schema.model_validate(response.json())
    operations: list[str] = []
    undocumented = faulty = internal = versioned = 0
    for path, item in schema.paths.items():
        for method, raw in item.items():
            if method not in METHODS:
                continue
            operation = Operation.model_validate(raw)
            operations.append(f"{method.upper()} {path}")
            undocumented += not (operation.summary or operation.description)
            versioned += "/v2/" in path
            internal += path.startswith(INTERNAL_PREFIXES)
            fault = str(operation.responses.get("500", ""))
            faulty += any(word in fault.lower() for word in FAULT_WORDS)
    fingerprint = hashlib.sha256("\n".join(sorted(operations)).encode()).hexdigest()[
        :12
    ]
    return ContractSnapshot(
        facts={
            "version": schema.info.version,
            "operations": len(operations),
            "v2_operations": versioned,
            "undocumented": undocumented,
            "faults_as_500": faulty,
            "internal_routes": internal,
            "fingerprint": fingerprint,
            "latency_ms": latency,
        },
        items=sorted(operations),
    )


async def observe_package(
    http: httpx.AsyncClient, contract: ProfileContract
) -> ContractSnapshot | None:
    registry = await http.get(
        f"https://registry.npmjs.org/{contract.id.replace('/', '%2F')}"
    )
    if registry.status_code != 200:
        return None
    release = Release.model_validate(registry.json())
    stamps = {
        version: stamp
        for version, stamp in release.time.items()
        if version not in {"created", "modified"}
    }
    latest_stamp = max(stamps.values()) if stamps else ""
    downloads = await http.get(
        f"https://api.npmjs.org/downloads/point/last-month/{contract.id}"
    )
    monthly = (
        downloads.json().get("downloads") if downloads.status_code == 200 else None
    )
    tags = ", ".join(f"{tag} {version}" for tag, version in release.dist_tags.items())
    return ContractSnapshot(
        facts={
            "tags": tags,
            "versions": len(release.versions),
            "published": latest_stamp[:10],
            "downloads_month": monthly,
        },
        items=sorted(release.versions)[-12:],
    )


async def observe_repo(
    http: httpx.AsyncClient, contract: ProfileContract
) -> ContractSnapshot | None:
    response = await http.get(
        f"https://api.github.com/repos/{contract.id}",
        headers={"Accept": "application/vnd.github+json"},
    )
    if response.status_code != 200:
        return None
    repository = Repository.model_validate(response.json())
    return ContractSnapshot(
        facts={
            "open_issues": repository.open_issues_count,
            "stars": repository.stargazers_count,
            "forks": repository.forks_count,
            "pushed": repository.pushed_at[:10],
            "archived": "TRUE" if repository.archived else "FALSE",
        }
    )


async def observe_wasm(
    http: httpx.AsyncClient, network: Network, contract: ProfileContract
) -> ContractSnapshot | None:
    key = xdr.LedgerKey(
        type=xdr.LedgerEntryType.CONTRACT_CODE,
        contract_code=xdr.LedgerKeyContractCode(
            hash=xdr.Hash(bytes.fromhex(contract.id))
        ),
    )
    result = await SorobanRpc(http, network.rpc_url).call(
        "getLedgerEntries", {"keys": [key.to_xdr()]}
    )
    entries = result.get("entries") or []
    if not entries:
        return ContractSnapshot(facts={"live": "FALSE"})
    code = xdr.LedgerEntryData.from_xdr(entries[0]["xdr"]).contract_code.code
    present = [name for name in ESCROW_FUNCTIONS if name.encode() in code]
    return ContractSnapshot(facts={"live": "TRUE", "bytes": len(code)}, items=present)


class TrustlessWorkAdapter(Adapter):
    name = "trustless-work"

    async def observe(
        self, http: httpx.AsyncClient, network: Network, contract: ProfileContract
    ) -> ContractSnapshot | None:
        if contract.kind == "api":
            return await observe_api(http, contract)
        if contract.kind == "package":
            return await observe_package(http, contract)
        if contract.kind == "repo":
            return await observe_repo(http, contract)
        if contract.kind == "wasm":
            return await observe_wasm(http, network, contract)
        return None
