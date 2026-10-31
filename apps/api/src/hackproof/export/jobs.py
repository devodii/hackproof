import logging

from hackproof.config import ROOT
from hackproof.db import open_pool, pool
from hackproof.export.build import build_export
from hackproof.export.files import write_project_files
from hackproof.hackathon import get_hackathon

log = logging.getLogger("hackproof.export")

DATA = ROOT / "data"


async def run_export() -> None:
    hackathon = get_hackathon()
    await open_pool()
    async with pool().acquire() as connection:
        export = await build_export(connection, hackathon)

    count = write_project_files(export, DATA)
    log.info("wrote %s project files to %s", count, DATA / str(export.hackathon.starts_at.year))
