import hashlib
from datetime import UTC, datetime
from typing import Any

from stellar_sdk import MuxedAccount, StrKey, xdr

from hackproof.indexer.events import ClassicOp, Deploy, Event, Failure, Funding, Upload
from hackproof.indexer.wasm import contract_meta

OP = xdr.OperationType
UPLOAD = xdr.HostFunctionType.HOST_FUNCTION_TYPE_UPLOAD_CONTRACT_WASM
CREATE = xdr.HostFunctionType.HOST_FUNCTION_TYPE_CREATE_CONTRACT
CREATE_V2 = xdr.HostFunctionType.HOST_FUNCTION_TYPE_CREATE_CONTRACT_V2
FROM_ADDRESS = xdr.ContractIDPreimageType.CONTRACT_ID_PREIMAGE_FROM_ADDRESS
WASM_EXECUTABLE = xdr.ContractExecutableType.CONTRACT_EXECUTABLE_WASM

ASSET_FIELDS: dict[xdr.OperationType, tuple[str, tuple[str, ...]]] = {
    OP.PAYMENT: ("payment_op", ("asset",)),
    OP.PATH_PAYMENT_STRICT_RECEIVE: ("path_payment_strict_receive_op", ("dest_asset",)),
    OP.PATH_PAYMENT_STRICT_SEND: ("path_payment_strict_send_op", ("dest_asset",)),
    OP.CHANGE_TRUST: ("change_trust_op", ("line",)),
    OP.MANAGE_SELL_OFFER: ("manage_sell_offer_op", ("selling", "buying")),
    OP.MANAGE_BUY_OFFER: ("manage_buy_offer_op", ("selling", "buying")),
    OP.CREATE_PASSIVE_SELL_OFFER: ("create_passive_sell_offer_op", ("selling", "buying")),
    OP.CREATE_CLAIMABLE_BALANCE: ("create_claimable_balance_op", ("asset",)),
    OP.SET_TRUST_LINE_FLAGS: ("set_trust_line_flags_op", ("asset",)),
}
PLAIN_CLASSIC = {
    OP.SET_OPTIONS,
    OP.MANAGE_DATA,
    OP.LIQUIDITY_POOL_DEPOSIT,
    OP.LIQUIDITY_POOL_WITHDRAW,
    OP.CLAIM_CLAIMABLE_BALANCE,
    OP.ACCOUNT_MERGE,
    OP.CLAWBACK,
}
RECIPIENT_FIELDS = {
    OP.PAYMENT: "payment_op",
    OP.PATH_PAYMENT_STRICT_RECEIVE: "path_payment_strict_receive_op",
    OP.PATH_PAYMENT_STRICT_SEND: "path_payment_strict_send_op",
}


def _inner_transaction(envelope: xdr.TransactionEnvelope) -> Any:
    if envelope.fee_bump is not None:
        return envelope.fee_bump.tx.inner_tx.v1.tx
    if envelope.v1 is not None:
        return envelope.v1.tx
    return envelope.v0.tx


def _transaction_source(transaction: Any) -> str:
    if hasattr(transaction, "source_account_ed25519"):
        return StrKey.encode_ed25519_public_key(transaction.source_account_ed25519.uint256)
    return MuxedAccount.from_xdr_object(transaction.source_account).account_id


def _operation_source(operation: xdr.Operation, default: str) -> str:
    if operation.source_account is None:
        return default
    return MuxedAccount.from_xdr_object(operation.source_account).account_id


def _account_id(account: xdr.AccountID) -> str:
    return StrKey.encode_ed25519_public_key(account.account_id.ed25519.uint256)


def _asset_label(asset: Any) -> str | None:
    for credit, code_field in (
        (asset.alpha_num4, "asset_code4"),
        (asset.alpha_num12, "asset_code12"),
    ):
        if credit is not None:
            code = getattr(credit.asset_code, code_field).rstrip(b"\0").decode()
            return f"{code}:{_account_id(credit.issuer)}"
    return None


def _classic_asset(operation: xdr.Operation) -> str | None:
    field = ASSET_FIELDS.get(operation.body.type)
    if field is None:
        return None
    body = getattr(operation.body, field[0])
    labels = (_asset_label(getattr(body, name)) for name in field[1])
    return next((label for label in labels if label), None)


def _counterparty(operation: xdr.Operation) -> str | None:
    field = RECIPIENT_FIELDS.get(operation.body.type)
    if field is None:
        return None
    return MuxedAccount.from_xdr_object(getattr(operation.body, field).destination).account_id


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


def _host_function_event(
    function: xdr.HostFunction,
    source: str,
    network_id: bytes,
    tx_hash: str,
    ledger: int,
    at: datetime,
) -> Event | None:
    if function.type == UPLOAD:
        wasm = function.wasm
        return Upload(
            wasm_hash=hashlib.sha256(wasm).hexdigest(),
            uploader=source,
            size=len(wasm),
            meta=contract_meta(wasm),
            tx_hash=tx_hash,
            ledger=ledger,
            at=at,
        )
    if function.type in (CREATE, CREATE_V2):
        args = function.create_contract if function.type == CREATE else function.create_contract_v2
        if (
            args.contract_id_preimage.type != FROM_ADDRESS
            or args.executable.type != WASM_EXECUTABLE
        ):
            return None
        contract_id = _contract_id(args.contract_id_preimage, network_id)
        return Deploy(
            contract_id=contract_id,
            deployer=source,
            wasm_hash=args.executable.wasm_hash.hash.hex(),
            tx_hash=tx_hash,
            ledger=ledger,
            at=at,
        )
    return None


def parse_transaction(raw: dict[str, Any], network_id: bytes) -> list[Event]:
    envelope = xdr.TransactionEnvelope.from_xdr(raw["envelopeXdr"])
    transaction = _inner_transaction(envelope)
    default_source = _transaction_source(transaction)
    tx_hash, ledger = raw["txHash"], raw["ledger"]
    at = datetime.fromtimestamp(int(raw["createdAt"]), UTC)
    failed = raw["status"] != "SUCCESS"
    events: list[Event] = []
    failure_kind: str | None = None

    for index, operation in enumerate(transaction.operations):
        source = _operation_source(operation, default_source)
        op_type = operation.body.type

        if op_type == OP.INVOKE_HOST_FUNCTION:
            function = operation.body.invoke_host_function_op.host_function
            failure_kind = failure_kind or _kind(function.type)
            if not failed and (
                event := _host_function_event(function, source, network_id, tx_hash, ledger, at)
            ):
                events.append(event)
        elif failed:
            continue
        elif op_type == OP.CREATE_ACCOUNT:
            destination = _account_id(operation.body.create_account_op.destination)
            events.append(
                Funding(account=destination, funder=source, tx_hash=tx_hash, ledger=ledger, at=at)
            )
        elif op_type in ASSET_FIELDS or op_type in PLAIN_CLASSIC:
            events.append(
                ClassicOp(
                    tx_hash=tx_hash,
                    index=index,
                    source_account=source,
                    op_type=op_type.name.lower(),
                    asset=_classic_asset(operation),
                    counterparty=_counterparty(operation),
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
