import argparse
import asyncio
import logging
from pathlib import Path

from hackproof.export.jobs import run_export
from hackproof.github.jobs import run_discover, run_scan
from hackproof.hackathon import scaffold_hackathon
from hackproof.indexer.sync import run_sync
from hackproof.linking.reconcile import run_reconcile


def _prompt_if_missing(value: str | None, label: str) -> str:
    if value:
        return value
    return input(f"{label}: ").strip()


def run_new_hackathon(args: argparse.Namespace) -> Path:
    slug = _prompt_if_missing(args.slug, "Hackathon slug (e.g. hackmeridian-2027)")
    name = _prompt_if_missing(args.name, "Hackathon name (e.g. HackMeridian 2027)")
    start = _prompt_if_missing(args.start, "Window start UTC (e.g. 2027-10-25T09:00:00Z)")
    end = _prompt_if_missing(args.end, "Window end UTC (e.g. 2027-10-26T12:00:00Z)")
    output_dir = Path(args.output_dir) if args.output_dir else None
    path = scaffold_hackathon(
        slug=slug,
        name=name,
        start=start,
        end=end,
        pull_start=args.pull_start,
        output_dir=output_dir,
    )
    print(f"Wrote {path}")
    print("Next steps:")
    print(f"  export HACKPROOF_HACKATHON_FILE={path}")
    print("  uv run hackproof sync")
    print("  uv run hackproof discover")
    print("  uv run hackproof scan")
    print("  uv run hackproof reconcile")
    print("  uv run hackproof export")
    return path


def main(argv: list[str] | None = None) -> None:
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
    commands.add_parser("export", help="write one yaml file per project into data and its schema")
    new_hack = commands.add_parser("new-hackathon", help="scaffold a new hackathon yaml config")
    new_hack.add_argument("--slug", help="event slug, e.g. hackmeridian-2027")
    new_hack.add_argument("--name", help="event display name, e.g. HackMeridian 2027")
    new_hack.add_argument("--start", help="official window start, ISO 8601 UTC")
    new_hack.add_argument("--end", help="official submission deadline, ISO 8601 UTC")
    new_hack.add_argument("--pull-start", help="ledger pull start, ISO 8601 UTC")
    new_hack.add_argument("--output-dir", help="directory to write the yaml file into")
    args = parser.parse_args(argv)

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
            run_new_hackathon(args)
