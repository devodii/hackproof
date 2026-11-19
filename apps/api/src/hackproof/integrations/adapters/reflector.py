import asyncio
import time
from decimal import Decimal
from typing import Any

from stellar_sdk import StrKey, scval, xdr

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot, Quote
from hackproof.integrations.soroban import view


def asset_key(native: Any) -> str:
    kind, value = native
    return str(getattr(value, "address", value)) if kind == "Stellar" else str(value)


def asset_arg(contract: ProfileContract, asset: str) -> xdr.SCVal:
    if contract.attributes.get("asset_kind") == "stellar" and StrKey.is_valid_contract(
        asset
    ):
        return scval.to_enum("Stellar", scval.to_address(asset))
    return scval.to_enum("Other", scval.to_symbol(asset))


async def observe(
    rpc: SorobanRpc, network: Network, contract: ProfileContract
) -> ContractSnapshot | None:
    if contract.kind != "feed":
        return None

    async def read(function: str) -> Any:
        return await view(rpc, network.passphrase, contract.id, function)

    base, decimals, resolution, retention, version, last, assets = await asyncio.gather(
        read("base"),
        read("decimals"),
        read("resolution"),
        read("history_retention_period"),
        read("version"),
        read("last_timestamp"),
        read("assets"),
    )
    return ContractSnapshot(
        base=asset_key(base) if base else None,
        decimals=decimals,
        resolution=resolution,
        retention=retention,
        version=version,
        last_timestamp=last,
        assets=[asset_key(item) for item in assets or []],
    )


async def quote(
    rpc: SorobanRpc,
    network: Network,
    contract: ProfileContract,
    asset: str,
    age_factor: int,
) -> Quote | None:
    decimals, resolution, last = await asyncio.gather(
        view(rpc, network.passphrase, contract.id, "decimals"),
        view(rpc, network.passphrase, contract.id, "resolution"),
        view(
            rpc,
            network.passphrase,
            contract.id,
            "lastprice",
            [asset_arg(contract, asset)],
        ),
    )
    if not last:
        return None
    age = max(0, int(time.time()) - last["timestamp"])
    return Quote(
        contract=contract.slug,
        asset=asset,
        price=format(Decimal(last["price"]) / Decimal(10) ** decimals, "f"),
        decimals=decimals,
        timestamp=last["timestamp"],
        age_seconds=age,
        stale=age > resolution * age_factor,
    )


class ReflectorAdapter(Adapter):
    name = "reflector"

    async def observe(
        self, rpc: SorobanRpc, network: Network, contract: ProfileContract
    ) -> ContractSnapshot | None:
        return await observe(rpc, network, contract)

    async def probe(
        self,
        rpc: SorobanRpc,
        network: Network,
        contract: ProfileContract,
        asset: str,
        params: dict[str, int],
    ) -> Quote | None:
        return await quote(rpc, network, contract, asset, params.get("age_factor", 2))
