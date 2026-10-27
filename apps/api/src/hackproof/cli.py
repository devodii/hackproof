import argparse
import asyncio
import logging

from hackproof.indexer.sync import run_sync
from hackproof.linking.link import run_link


def main() -> None:
    parser = argparse.ArgumentParser(prog="hackproof")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="index the hack window from testnet")
    commands.add_parser("link", help="link wasm to github repos")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    if args.command == "sync":
        asyncio.run(run_sync())
    elif args.command == "link":
        asyncio.run(run_link())
