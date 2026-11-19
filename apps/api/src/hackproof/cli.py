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
from hackproof.linking.reconcile import run_reconcile


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
        case "sync":
            asyncio.run(run_sync())
        case "discover":
            asyncio.run(run_discover(args.strings))
        case "scan":
            asyncio.run(run_scan(args.force, args.projects))
        case "reconcile":
            asyncio.run(run_reconcile())
        case "export":
            asyncio.run(run_export())
        case "import":
            raise SystemExit(run_restore(args))
        case "check":
            raise SystemExit(asyncio.run(run_check()))
        case "schema":
            raise SystemExit(run_schema(args))
