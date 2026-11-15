import asyncio
import hashlib
import logging
from collections import defaultdict
from datetime import UTC, datetime

import asyncpg
import httpx

from hackproof.config import get_settings
from hackproof.db import open_pool, pool
from hackproof.hackathon import get_hackathon
from hackproof.indexer.events import Event
from hackproof.indexer.horizon import Horizon
from hackproof.indexer.parser import parse_transaction
from hackproof.indexer.rpc import SorobanRpc
from hackproof.sql_loader import load_sql

log = logging.getLogger("hackproof.sync")

CHUNK_LEDGERS = 400
CHUNK_PREFIX = "chunk:v2:"
DEADLOCK_RETRIES = 5


def ensure_within_retention(pull_start: datetime, oldest_closed_at: datetime) -> None:
    if pull_start < oldest_closed_at:
        raise RuntimeError(
            f"the event window starts {pull_start:%Y-%m-%d %H:%M} UTC, before the oldest ledger "
            f"the RPC still holds ({oldest_closed_at:%Y-%m-%d %H:%M} UTC); the RPC keeps about "
            "7 days, so this window can no longer be synced"
        )


async def _fetch_chunk(
    rpc: SorobanRpc, network_id: bytes, start: int, end: int
) -> list[Event]:
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


async def _store(events: list[Event], chunk_key: str) -> None:
    for attempt in range(DEADLOCK_RETRIES):
        try:
            async with pool().acquire() as connection:
                return await _insert(connection, events, chunk_key)
        except asyncpg.DeadlockDetectedError:
            await asyncio.sleep(attempt + 1)
    raise RuntimeError(f"{chunk_key} kept deadlocking")


async def _insert(
    connection: asyncpg.Connection, events: list[Event], chunk_key: str
) -> None:
    by_table: dict[str, list[Event]] = defaultdict(list)
    for event in events:
        by_table[event.table].append(event)
    async with connection.transaction():
        for table, rows in sorted(by_table.items()):
            await connection.executemany(
                load_sql(f"indexer/insert_{table}"),
                [event.row() for event in rows],
            )
        await connection.execute(
            load_sql("indexer/insert_sync_state"),
            chunk_key,
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
        ensure_within_retention(
            window.pull_start,
            datetime.fromtimestamp(int(health["oldestLedgerCloseTime"]), tz=UTC),
        )
        first = await horizon.first_ledger_at_or_after(
            window.pull_start, oldest, latest
        )
        last = await horizon.first_ledger_at_or_after(window.end, first, latest) - 1
        log.info("syncing ledgers %s to %s", first, last)

        starts = list(range(first, last + 1, CHUNK_LEDGERS))
        async with pool().acquire() as connection:
            done = {
                row["key"]
                for row in await connection.fetch(
                    load_sql("indexer/done_chunks"), f"{CHUNK_PREFIX}%"
                )
            }
        pending = [s for s in starts if f"{CHUNK_PREFIX}{s}" not in done]
        log.info("%s of %s chunks pending", len(pending), len(starts))

        semaphore = asyncio.Semaphore(settings.rpc_concurrency)
        completed = 0

        async def process(start: int) -> None:
            nonlocal completed
            async with semaphore:
                events = await _fetch_chunk(
                    rpc, network_id, start, min(start + CHUNK_LEDGERS - 1, last)
                )
            await _store(events, f"{CHUNK_PREFIX}{start}")
            completed += 1
            log.info(
                "chunk %s/%s done (%s events)", completed, len(pending), len(events)
            )

        await asyncio.gather(*(process(s) for s in pending))
