import asyncio
import hashlib
import json
import logging

import asyncpg
import httpx

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.hackathon import get_hackathon
from hackproof.indexer.horizon import Horizon
from hackproof.indexer.parser import Deploy, Event, Failure, Upload, parse_transaction
from hackproof.indexer.rpc import SorobanRpc

log = logging.getLogger("hackproof.sync")

CHUNK_LEDGERS = 400


async def _fetch_chunk(rpc: SorobanRpc, network_id: bytes, start: int, end: int) -> list[Event]:
    events: list[Event] = []
    page = await rpc.transactions(start_ledger=start)
    while page["transactions"]:
        for raw in page["transactions"]:
            if raw["ledger"] <= end:
                events.extend(parse_transaction(raw, network_id))
        if page["transactions"][-1]["ledger"] > end:
            break
        page = await rpc.transactions(cursor=page["cursor"])
    return events


async def _store(connection: asyncpg.Connection, events: list[Event], chunk_key: str) -> None:
    deploys = [e for e in events if isinstance(e, Deploy)]
    uploads = [e for e in events if isinstance(e, Upload)]
    failures = [e for e in events if isinstance(e, Failure)]
    async with connection.transaction():
        await connection.executemany(
            "INSERT INTO contracts VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
            [(e.contract_id, e.deployer, e.wasm_hash, e.tx_hash, e.ledger, e.at) for e in deploys],
        )
        await connection.executemany(
            "INSERT INTO wasm_uploads VALUES ($1, $2, $3, $4, $5, $6::jsonb, $7, $8)"
            " ON CONFLICT DO NOTHING",
            [
                (
                    e.tx_hash,
                    e.wasm_hash,
                    e.uploader,
                    e.size,
                    e.meta.get("source_repo"),
                    json.dumps(e.meta),
                    e.ledger,
                    e.at,
                )
                for e in uploads
            ],
        )
        await connection.executemany(
            "INSERT INTO failed_txs VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
            [
                (e.tx_hash, e.source_account, e.kind, e.result_code, e.ledger, e.at)
                for e in failures
            ],
        )
        await connection.execute(
            "INSERT INTO sync_state VALUES ($1, 'done') ON CONFLICT DO NOTHING", chunk_key
        )


async def run_sync() -> None:
    settings = get_settings()
    network_id = hashlib.sha256(settings.network_passphrase.encode()).digest()
    await open_pool()

    async with httpx.AsyncClient(timeout=httpx.Timeout(90)) as client:
        rpc = SorobanRpc(client, settings.soroban_rpc_url)
        horizon = Horizon(client, settings.horizon_url)

        health = await rpc.call("getHealth")
        oldest, latest = health["oldestLedger"], health["latestLedger"]
        window = get_hackathon().window
        first = await horizon.first_ledger_at_or_after(window.pull_start, oldest, latest)
        last = await horizon.first_ledger_at_or_after(window.end, first, latest) - 1
        log.info("syncing ledgers %s to %s", first, last)

        starts = list(range(first, last + 1, CHUNK_LEDGERS))
        async with pool().acquire() as connection:
            done = {
                row["key"]
                for row in await connection.fetch(
                    "SELECT key FROM sync_state WHERE key LIKE 'chunk:%'"
                )
            }
        pending = [s for s in starts if f"chunk:{s}" not in done]
        log.info("%s of %s chunks pending", len(pending), len(starts))

        semaphore = asyncio.Semaphore(settings.rpc_concurrency)
        completed = 0

        async def process(start: int) -> None:
            nonlocal completed
            async with semaphore:
                events = await _fetch_chunk(
                    rpc, network_id, start, min(start + CHUNK_LEDGERS - 1, last)
                )
            async with pool().acquire() as connection:
                await _store(connection, events, f"chunk:{start}")
            completed += 1
            log.info("chunk %s/%s done (%s events)", completed, len(pending), len(events))

        await asyncio.gather(*(process(s) for s in pending))
