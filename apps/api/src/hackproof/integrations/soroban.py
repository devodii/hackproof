from typing import Any

from stellar_sdk import Account, Keypair, TransactionBuilder, scval, xdr

from hackproof.indexer.rpc import RpcError, SorobanRpc


async def view(
    rpc: SorobanRpc,
    passphrase: str,
    contract_id: str,
    function: str,
    args: list[xdr.SCVal] | None = None,
) -> Any:
    transaction = (
        TransactionBuilder(Account(Keypair.random().public_key, 0), passphrase, 100)
        .add_time_bounds(0, 0)
        .append_invoke_contract_function_op(contract_id, function, args or [])
        .build()
    )
    result = await rpc.call(
        "simulateTransaction", {"transaction": transaction.to_xdr()}
    )
    if "error" in result:
        raise RpcError(result["error"])
    results = result.get("results") or []
    if not results:
        return None
    return scval.to_native(xdr.SCVal.from_xdr(results[0]["xdr"]))
