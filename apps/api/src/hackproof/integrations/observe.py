import logging
from datetime import UTC, datetime

import httpx
from stellar_sdk import Asset

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.indexer.rpc import RpcError
from hackproof.integrations.adapters import ADAPTERS
from hackproof.integrations.catalog import Product, ProfileContract, get_catalog
from hackproof.sql_loader import load_sql

log = logging.getLogger("hackproof.integrations")


async def observe_item(
    http: httpx.AsyncClient, partner: Product, contract: ProfileContract
) -> bool:
    profile = partner.profile
    if profile is None or profile.adapter not in ADAPTERS:
        return False
    network = profile.networks[contract.network]
    try:
        snapshot = await ADAPTERS[profile.adapter].observe(http, network, contract)
    except (RpcError, httpx.HTTPError):
        log.warning("could not read %s %s", partner.slug, contract.slug)
        return False
    if snapshot is None:
        return False
    async with pool().acquire() as connection:
        await connection.execute(
            load_sql("integrations/upsert_contract"),
            partner.slug,
            contract.id,
            contract.network,
            snapshot.model_dump(),
            datetime.now(UTC),
        )
    log.info(
        "observed %s %s: %s items", partner.slug, contract.slug, len(snapshot.items)
    )
    return True


async def run_observe() -> None:
    catalog = get_catalog()
    await open_pool()
    async with httpx.AsyncClient(timeout=30) as http:
        for partner in [*catalog.partners, *catalog.tools]:
            profile = partner.profile
            if profile is None:
                continue
            for contract in [*profile.contracts, *profile.surfaces]:
                await observe_item(http, partner, contract)
    await map_assets()


async def map_assets() -> None:
    passphrase = get_settings().network_passphrase
    async with pool().acquire() as connection:
        rows = await connection.fetch(load_sql("integrations/unmapped_assets"))
        pairs = []
        for row in rows:
            code, _, issuer = row["asset"].partition(":")
            pairs.append((row["asset"], Asset(code, issuer).contract_id(passphrase)))
        await connection.executemany(
            load_sql("integrations/insert_asset_contract"), pairs
        )
    log.info("mapped %s assets to their contracts", len(pairs))
