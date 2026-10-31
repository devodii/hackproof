import argparse
import asyncio
import logging

from hackproof.export.jobs import run_export
from hackproof.github.jobs import run_discover, run_scan
from hackproof.indexer.sync import run_sync
from hackproof.linking.reconcile import run_reconcile
from hackproof.scaffold import run_new_hackathon_interactive


def main() -> None:
    parser = argparse.ArgumentParser(prog="hackproof")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="index the hack window from testnet")
    discover = commands.add_parser("discover", help="find candidate repos on github")
    discover.add_argument(
        "--strings", action="store_true", help="also run the network string code queries"
    )
    scan = commands.add_parser("scan", help="scan discovered repos for chain fingerprints")
    scan.add_argument("--force", action="store_true", help="rescan repos already scanned")
    scan.add_argument(
        "--projects", action="store_true", help="only scan repos that are already projects"
    )
    commands.add_parser("reconcile", help="link chain activity to repos and build projects")
    commands.add_parser("export", help="write the json and yaml export and its schema")

    new_hackathon = commands.add_parser(
        "new-hackathon", help="scaffold configuration for a new hackathon event"
    )
    new_hackathon.add_argument("--slug", help="hackathon slug (e.g. hacklisbon-2027)")
    new_hackathon.add_argument("--name", help="hackathon display name (e.g. HackLisbon 2027)")
    new_hackathon.add_argument(
        "--start", help="hack window start datetime (e.g. 2027-04-10T09:00:00Z)"
    )
    new_hackathon.add_argument("--end", help="hack window end datetime (e.g. 2027-04-11T18:00:00Z)")
    new_hackathon.add_argument(
        "--pull-start", help="optional pull start datetime (default: 1 hour before start)"
    )
    new_hackathon.add_argument(
        "--output", "-o", help="output file path (default: config/{slug}.yaml)"
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
        case "new-hackathon":
            run_new_hackathon_interactive(
                slug=args.slug,
                name=args.name,
                start=args.start,
                end=args.end,
                pull_start=args.pull_start,
                output=args.output,
            )
