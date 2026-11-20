import logging
import time
from collections.abc import Awaitable, Callable, Sequence

from pydantic import BaseModel, ConfigDict

from hackproof.db import close_pool
from hackproof.export.jobs import run_export
from hackproof.github.jobs import run_discover, run_scan
from hackproof.indexer.sync import run_sync
from hackproof.integrations.observe import run_observe
from hackproof.linking.reconcile import run_reconcile

log = logging.getLogger("hackproof.pipeline")


class Stage(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    help: str
    run: Callable[[], Awaitable[None]]


class Options(BaseModel):
    strings: bool = False
    force: bool = False
    projects_only: bool = False


def stages(options: Options) -> list[Stage]:
    return [
        Stage(
            name="sync",
            help="index the hack window from the chain",
            run=run_sync,
        ),
        Stage(
            name="discover",
            help="find candidate repos on github",
            run=lambda: run_discover(options.strings),
        ),
        Stage(
            name="scan",
            help="scan the repos for chain fingerprints, integrations, tools and agents",
            run=lambda: run_scan(options.force, options.projects_only),
        ),
        Stage(
            name="reconcile",
            help="link chain activity to repos and build the projects",
            run=run_reconcile,
        ),
        Stage(
            name="observe",
            help="read the live state of the integrations' contracts",
            run=run_observe,
        ),
        Stage(
            name="export",
            help="write the project files into data",
            run=run_export,
        ),
    ]


def select(
    available: Sequence[Stage],
    *,
    only: Sequence[str] = (),
    skip: Sequence[str] = (),
    start: str | None = None,
) -> list[Stage]:
    names = [stage.name for stage in available]
    unknown = [
        name
        for name in [*only, *skip, *([start] if start else [])]
        if name not in names
    ]
    if unknown:
        raise ValueError(
            f"unknown stage {', '.join(unknown)}; the stages are {', '.join(names)}"
        )
    chosen = list(available)
    if start:
        chosen = chosen[names.index(start) :]
    if only:
        chosen = [stage for stage in chosen if stage.name in only]
    return [stage for stage in chosen if stage.name not in skip]


async def run_pipeline(chosen: Sequence[Stage]) -> None:
    started = time.monotonic()
    log.info("running %s", ", ".join(stage.name for stage in chosen))
    for index, stage in enumerate(chosen, start=1):
        log.info("[%s/%s] %s: %s", index, len(chosen), stage.name, stage.help)
        began = time.monotonic()
        try:
            await stage.run()
        except Exception:
            log.error(
                "%s failed; fix it and carry on with: hackproof run --from %s",
                stage.name,
                stage.name,
            )
            raise
        finally:
            await close_pool()
        log.info("%s done in %.0fs", stage.name, time.monotonic() - began)
    log.info("pipeline done in %.0fs", time.monotonic() - started)
