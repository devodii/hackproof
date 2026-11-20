import argparse
import asyncio
import logging
import os
from pathlib import Path

from hackproof.config import get_settings
from hackproof.db_utils import pgschema
from hackproof.db_utils.connection import Connection
from hackproof.export.jobs import run_check, run_export, run_import
from hackproof.github.jobs import run_discover, run_scan
from hackproof.indexer.sync import run_sync
from hackproof.integrations.observe import run_observe
from hackproof.linking.reconcile import run_reconcile
from hackproof.openapi import write as write_openapi
from hackproof.pipeline import Options, WrongEvent, run_pipeline, select, stages


def run_schema(args: argparse.Namespace) -> int:
    connection = Connection.from_url(get_settings().database_url)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("\n".join(connection.mask_lines()), flush=True)
    match args.action:
        case "plan":
            return pgschema.plan(connection)
        case "apply":
            if not (connection.is_local or args.remote or os.environ.get("CI")):
                print(
                    f"{connection.label} is not on this machine. Pass --remote to apply "
                    "to it, or let CI do it on merge."
                )
                return 1
            return pgschema.apply(
                connection,
                allow_destructive=args.allow_destructive,
                out_dir=args.out_dir,
            )
        case "verify":
            return pgschema.verify(connection)
    return 1


def run_all(args: argparse.Namespace) -> int:
    if args.hackathon:
        os.environ["HACKPROOF_HACKATHON_FILE"] = str(args.hackathon.resolve())
    connection = Connection.from_url(get_settings().database_url)
    if not (connection.is_local or args.remote):
        print(
            f"{connection.label} is not on this machine. Pass --remote to run the "
            "pipeline against it."
        )
        return 1
    try:
        chosen = select(
            stages(
                Options(
                    strings=args.strings, force=args.force, projects_only=args.projects
                )
            ),
            only=args.only,
            skip=args.skip,
            start=args.start,
        )
    except ValueError as error:
        print(error)
        return 1
    try:
        asyncio.run(run_pipeline(chosen))
    except WrongEvent as error:
        print(error)
        return 1
    return 0


def run_restore(args: argparse.Namespace) -> int:
    connection = Connection.from_url(get_settings().database_url)
    if not (connection.is_local or args.remote or os.environ.get("CI")):
        print(
            f"{connection.label} is not on this machine. Pass --remote to write to it, "
            "or let CI do it on merge."
        )
        return 1
    asyncio.run(run_import())
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="hackproof")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser(
        "run",
        help="run the whole pipeline for a hackathon: sync, discover, scan, reconcile, observe, export",
    )
    run.add_argument(
        "--hackathon",
        type=Path,
        help="the hackathon file to run, default data/hackmeridian-2026/main.yaml",
    )
    run.add_argument("--from", dest="start", help="start at this stage and carry on")
    run.add_argument("--only", nargs="+", default=[], help="run only these stages")
    run.add_argument("--skip", nargs="+", default=[], help="leave these stages out")
    run.add_argument(
        "--strings",
        action="store_true",
        help="also run the network string code queries",
    )
    run.add_argument(
        "--force", action="store_true", help="rescan repos already scanned"
    )
    run.add_argument(
        "--projects",
        action="store_true",
        help="only scan repos that are already projects",
    )
    run.add_argument(
        "--remote",
        action="store_true",
        help="allow a database that is not on this machine",
    )
    commands.add_parser("sync", help="index the hack window from testnet")
    discover = commands.add_parser("discover", help="find candidate repos on github")
    discover.add_argument(
        "--strings",
        action="store_true",
        help="also run the network string code queries",
    )
    scan = commands.add_parser(
        "scan", help="scan discovered repos for chain fingerprints"
    )
    scan.add_argument(
        "--force", action="store_true", help="rescan repos already scanned"
    )
    scan.add_argument(
        "--projects",
        action="store_true",
        help="only scan repos that are already projects",
    )
    commands.add_parser(
        "observe",
        help="read the live state of each partner's contracts and map assets to their contracts",
    )
    commands.add_parser(
        "reconcile", help="link chain activity to repos and build projects"
    )
    commands.add_parser(
        "export", help="write one yaml file per project into data and its schema"
    )
    restore = commands.add_parser(
        "import",
        help="load the integrations, tools and agents of the committed project files into the database",
    )
    restore.add_argument(
        "--remote",
        action="store_true",
        help="allow a database that is not on this machine",
    )
    commands.add_parser(
        "openapi",
        help="write the api's openapi schema where the web app generates its types from",
    )
    commands.add_parser(
        "check",
        help="check, read-only, that the database matches the committed data files",
    )
    schema = commands.add_parser(
        "schema", help="manage the database schema with pgschema"
    )
    actions = schema.add_subparsers(dest="action", required=True)
    actions.add_parser(
        "plan", help="write the pending changes to the next numbered migration file"
    )
    apply = actions.add_parser(
        "apply", help="apply the schema files, refusing any change that could lose data"
    )
    apply.add_argument(
        "--allow-destructive",
        action="store_true",
        help="apply a plan that drops or rewrites data",
    )
    apply.add_argument(
        "--remote",
        action="store_true",
        help="allow a database that is not on this machine",
    )
    apply.add_argument("--out-dir", type=Path, help="keep plan.json and plan.sql here")
    actions.add_parser(
        "verify", help="fail unless the manifest is current and nothing is pending"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    match args.command:
        case "run":
            raise SystemExit(run_all(args))
        case "sync":
            asyncio.run(run_sync())
        case "discover":
            asyncio.run(run_discover(args.strings))
        case "scan":
            asyncio.run(run_scan(args.force, args.projects))
        case "observe":
            asyncio.run(run_observe())
        case "reconcile":
            asyncio.run(run_reconcile())
        case "export":
            asyncio.run(run_export())
        case "import":
            raise SystemExit(run_restore(args))
        case "openapi":
            write_openapi()
        case "check":
            raise SystemExit(asyncio.run(run_check()))
        case "schema":
            raise SystemExit(run_schema(args))
