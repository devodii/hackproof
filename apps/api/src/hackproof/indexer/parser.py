import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from stellar_sdk import MuxedAccount, StrKey, xdr

from hackproof.indexer.wasm import contract_meta

HOST_FUNCTION = xdr.OperationType.INVOKE_HOST_FUNCTION
UPLOAD = xdr.HostFunctionType.HOST_FUNCTION_TYPE_UPLOAD_CONTRACT_WASM
CREATE = xdr.HostFunctionType.HOST_FUNCTION_TYPE_CREATE_CONTRACT
CREATE_V2 = xdr.HostFunctionType.HOST_FUNCTION_TYPE_CREATE_CONTRACT_V2
FROM_ADDRESS = xdr.ContractIDPreimageType.CONTRACT_ID_PREIMAGE_FROM_ADDRESS
WASM_EXECUTABLE = xdr.ContractExecutableType.CONTRACT_EXECUTABLE_WASM


@dataclass(frozen=True)
class Deploy:
    contract_id: str
    deployer: str
    wasm_hash: str
    tx_hash: str
    ledger: int
    at: datetime


@dataclass(frozen=True)
class Upload:
    wasm_hash: str
    uploader: str
    size: int
    meta: dict[str, str]
    tx_hash: str
    ledger: int
    at: datetime


@dataclass(frozen=True)
class Failure:
    tx_hash: str
    source_account: str
    kind: str
    result_code: str
    ledger: int
    at: datetime


Event = Deploy | Upload | Failure


def _inner_transaction(envelope: xdr.TransactionEnvelope) -> xdr.Transaction | xdr.TransactionV0:
    if envelope.fee_bump is not None:
        return envelope.fee_bump.tx.inner_tx.v1.tx
    if envelope.v1 is not None:
        return envelope.v1.tx
    return envelope.v0.tx


def _source(transaction: Any) -> str:
    if hasattr(transaction, "source_account_ed25519"):
        return StrKey.encode_ed25519_public_key(transaction.source_account_ed25519.uint256)
    return MuxedAccount.from_xdr_object(transaction.source_account).account_id


def _operation_source(operation: xdr.Operation, default: str) -> str:
    if operation.source_account is None:
        return default
    return MuxedAccount.from_xdr_object(operation.source_account).account_id


def _contract_id(preimage: xdr.ContractIDPreimage, network_id: bytes) -> str:
    wrapped = xdr.HashIDPreimage(
        type=xdr.EnvelopeType.ENVELOPE_TYPE_CONTRACT_ID,
        contract_id=xdr.HashIDPreimageContractID(
            network_id=xdr.Hash(network_id), contract_id_preimage=preimage
        ),
    )
    return StrKey.encode_contract(hashlib.sha256(wrapped.to_xdr_bytes()).digest())


def _result_code(result_xdr: str) -> str:
    result = xdr.TransactionResult.from_xdr(result_xdr)
    code = result.result.code.name.removeprefix("tx")
    inner = result.result.results or (
        result.result.inner_result_pair.result.result.results
        if result.result.inner_result_pair is not None
        else None
    )
    if inner and inner[0].tr is not None and inner[0].tr.invoke_host_function_result is not None:
        return inner[0].tr.invoke_host_function_result.code.name.removeprefix(
            "INVOKE_HOST_FUNCTION_"
        )
    return code


def _kind(function_type: xdr.HostFunctionType) -> str:
    if function_type == UPLOAD:
        return "upload"
    if function_type in (CREATE, CREATE_V2):
        return "deploy"
    return "invoke"


def parse_transaction(raw: dict[str, Any], network_id: bytes) -> list[Event]:
    envelope = xdr.TransactionEnvelope.from_xdr(raw["envelopeXdr"])
    transaction = _inner_transaction(envelope)
    default_source = _source(transaction)
    at = datetime.fromtimestamp(int(raw["createdAt"]), UTC)
    ledger = raw["ledger"]
    tx_hash = raw["txHash"]
    failed = raw["status"] != "SUCCESS"
    events: list[Event] = []
    failure_kind: str | None = None

    for operation in transaction.operations:
        if operation.body.type != HOST_FUNCTION:
            continue
        function = operation.body.invoke_host_function_op.host_function
        source = _operation_source(operation, default_source)
        failure_kind = failure_kind or _kind(function.type)
        if failed:
            continue
        if function.type == UPLOAD:
            wasm = function.wasm
            events.append(
                Upload(
                    wasm_hash=hashlib.sha256(wasm).hexdigest(),
                    uploader=source,
                    size=len(wasm),
                    meta=contract_meta(wasm),
                    tx_hash=tx_hash,
                    ledger=ledger,
                    at=at,
                )
            )
        elif function.type in (CREATE, CREATE_V2):
            args = (
                function.create_contract if function.type == CREATE else function.create_contract_v2
            )
            if args.contract_id_preimage.type != FROM_ADDRESS:
                continue
            if args.executable.type != WASM_EXECUTABLE:
                continue
            events.append(
                Deploy(
                    contract_id=_contract_id(args.contract_id_preimage, network_id),
                    deployer=source,
                    wasm_hash=args.executable.wasm_hash.hash.hex(),
                    tx_hash=tx_hash,
                    ledger=ledger,
                    at=at,
                )
            )

    if failed and failure_kind is not None:
        events.append(
            Failure(
                tx_hash=tx_hash,
                source_account=default_source,
                kind=failure_kind,
                result_code=_result_code(raw["resultXdr"]),
                ledger=ledger,
                at=at,
            )
        )
    return events
