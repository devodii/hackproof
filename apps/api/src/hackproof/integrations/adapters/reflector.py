import asyncio
import time
from decimal import Decimal
from typing import Any

from stellar_sdk import StrKey, scval, xdr

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.adapters.base import Adapter
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot, Reading
from hackproof.integrations.soroban import view

EXPIRY_CONCURRENCY = 8


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
    items = [asset_key(item) for item in assets or []]
    gate = asyncio.Semaphore(EXPIRY_CONCURRENCY)

    async def deadline(item: str) -> int | None:
        async with gate:
            return await view(
                rpc,
                network.passphrase,
                contract.id,
                "expires",
                [asset_arg(contract, item)],
            )

    deadlines = await asyncio.gather(*(deadline(item) for item in items))
    return ContractSnapshot(
        facts={
            "base": asset_key(base) if base else None,
            "decimals": decimals,
            "resolution": resolution,
            "retention": retention,
            "version": version,
            "last_timestamp": last,
        },
        items=items,
        deadlines={
            item: deadline
            for item, deadline in zip(items, deadlines, strict=True)
            if deadline
        },
    )


async def quote(
    rpc: SorobanRpc,
    network: Network,
    contract: ProfileContract,
    asset: str,
    age_factor: int,
) -> Reading | None:
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
        return Reading(
            contract=contract.slug,
            subject=asset,
            facts={"decimals": decimals, "resolution": resolution},
        )
    age = max(0, int(time.time()) - last["timestamp"])
    return Reading(
        contract=contract.slug,
        subject=asset,
        value=format(Decimal(last["price"]) / Decimal(10) ** decimals, "f"),
        timestamp=last["timestamp"],
        age_seconds=age,
        stale=age > resolution * age_factor,
        facts={"decimals": decimals, "resolution": resolution},
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
        subject: str,
        params: dict[str, int],
    ) -> Reading | None:
        return await quote(rpc, network, contract, subject, params.get("age_factor", 2))
