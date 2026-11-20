import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import asyncpg

from hackproof.config import ROOT, get_settings
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.check import drift
from hackproof.export.files import write_project_files
from hackproof.export.restore import load_files, restore
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

DATA = ROOT / "data"


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    count = write_project_files(export, DATA)
    log.info("wrote %s project files to %s", count, DATA / export.hackathon.slug)


async def run_check() -> int:
    hackathon = get_hackathon()
    connection = await asyncpg.connect(
        get_settings().database_url,
        server_settings={"default_transaction_read_only": "on"},
    )
    await connection.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )
    try:
        export = await build_export(connection, hackathon)
    finally:
        await connection.close()

    with TemporaryDirectory() as directory:
        write_project_files(export, Path(directory))
        found = drift(Path(directory), DATA)

    for line in found:
        log.warning(line)
    if found:
        log.warning("%s files differ from the database", len(found))
    else:
        log.info(
            "in sync: the database matches all %s project files", len(export.projects)
        )
    return 1 if found else 0


async def run_import() -> None:
    files = load_files(DATA)
    await open_pool()
    async with pool().acquire() as connection:
        count = await restore(connection, files)
    log.info("restored the scan data of %s projects from %s", count, DATA)
