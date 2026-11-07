import logging

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.files import write_api_schemas, write_project_files
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

DATA = ROOT / "data"
WEB_SCHEMA_DIR = ROOT / "apps" / "web" / "public" / "schema"


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    count = write_project_files(export, DATA)
    write_api_schemas(WEB_SCHEMA_DIR)
    log.info("wrote %s project files to %s", count, DATA / str(export.hackathon.starts_at.year))
