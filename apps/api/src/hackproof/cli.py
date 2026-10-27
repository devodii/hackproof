import argparse
import asyncio
import logging

from hackproof.github.jobs import run_discover, run_scan
from hackproof.indexer.sync import run_sync
from hackproof.linking.reconcile import run_reconcile


def main() -> None:
    parser = argparse.ArgumentParser(prog="hackproof")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="index the hack window from testnet")
    commands.add_parser("discover", help="find candidate repos on github")
    scan = commands.add_parser("scan", help="scan discovered repos for chain fingerprints")
    scan.add_argument("--force", action="store_true", help="rescan repos already scanned")
    commands.add_parser("reconcile", help="link chain activity to repos and build projects")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    match args.command:
        case "sync":
            asyncio.run(run_sync())
        case "discover":
            asyncio.run(run_discover())
        case "scan":
            asyncio.run(run_scan(args.force))
        case "reconcile":
            asyncio.run(run_reconcile())
