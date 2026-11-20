import hashlib
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field
from stellar_sdk import xdr

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.adapters.sources import observe_package, observe_repo
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot

METHODS = {"get", "post", "put", "patch", "delete"}
FAULT_WORDS = ("required", "must", "invalid", "not supported", "incomplete")
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
    undocumented = faulty = versioned = 0
    for path, item in schema.paths.items():
        for method, raw in item.items():
            if method not in METHODS:
                continue
            operation = Operation.model_validate(raw)
            operations.append(f"{method.upper()} {path}")
            undocumented += not (operation.summary or operation.description)
            versioned += "/v2/" in path
            fault = str(operation.responses.get("500", ""))
            faulty += any(word in fault.lower() for word in FAULT_WORDS)
    fingerprint = hashlib.sha256("\n".join(sorted(operations)).encode()).hexdigest()[
        :12
    ]
    return ContractSnapshot(
        facts={
            "operations": len(operations),
            "v2_operations": versioned,
            "undocumented": undocumented,
            "faults_as_500": faulty,
            "fingerprint": fingerprint,
            "latency_ms": latency,
        },
        items=sorted(operations),
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
