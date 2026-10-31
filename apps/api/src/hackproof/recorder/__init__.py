"""Continuous testnet recorder for HackProof.

Writes every ledger's transactions (including failed), operations and events to
object storage as gzip jsonl partitioned by date and hour:

    testnet/YYYY/MM/DD/HH/{ledgers,transactions,operations,events}.jsonl.gz

Keeps a cursor in object storage so a long running job / hourly cron can resume.
Idempotent: rerunning an hour overwrites the same keys. A manifest per day
lists the hours present and record counts. Reset detection writes resets.json.
"""

from __future__ import annotations

import gzip
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional

import boto3
from botocore.config import Config

from hackproof.events import Event

log = logging.getLogger("hackproof.recorder")

ARCHIVE_BUCKET = os.getenv("archive_bucket", os.getenv("ARCHIVE_BUCKET", ""))
ARCHIVE_ENDPOINT = os.getenv("archive_endpoint", os.getenv("ARCHIVE_ENDPOINT", ""))
ARCHIVE_KEY = os.getenv("archive_key", os.getenv("ARCHIVE_KEY", ""))
ARCHIVE_SECRET = os.getenv("archive_secret", os.getenv("ARCHIVE_SECRET", ""))


@dataclass
class Cursor:
    ledger: int
    updated_at: str


def _client():
    return boto3.client(
        "s3",
        endpoint_url=ARCHIVE_ENDPOINT or None,
        aws_access_key_id=ARCHIVE_KEY or None,
        aws_secret_access_key=ARCHIVE_SECRET or None,
        config=Config(signature_version="s3v4"),
    )


def _key(*parts: str) -> str:
    return "/".join(p.strip("/") for p in parts)


def cursor_key() -> str:
    return "testnet/cursor.json"


def load_cursor() -> Optional[Cursor]:
    try:
        obj = _client().get_object(Bucket=ARCHIVE_BUCKET, Key=cursor_key())
        data = json.loads(obj["Body"].read())
        return Cursor(ledger=int(data["ledger"]), updated_at=data["updated_at"])
    except Exception:
        return None


def save_cursor(ledger: int) -> None:
    c = Cursor(ledger=ledger, updated_at=datetime.now(timezone.utc).isoformat())
    _client().put_object(
        Bucket=ARCHIVE_BUCKET,
        Key=cursor_key(),
        Body=json.dumps(asdict(c)).encode(),
        ContentType="application/json",
    )


def _partition(dt: datetime) -> str:
    return f"testnet/{dt:%Y/%m/%d/%H}"


def _write_jsonl_gz(key: str, records: List[Dict[str, Any]]) -> None:
    buf = gzip.compress("\n".join(json.dumps(r) for r in records).encode() + (b"\n" if records else b""))
    _client().put_object(Bucket=ARCHIVE_BUCKET, Key=key, Body=buf, ContentType="application/gzip")


def _read_jsonl_gz(key: str) -> List[Dict[str, Any]]:
    try:
        obj = _client().get_object(Bucket=ARCHIVE_BUCKET, Key=key)
    except Exception:
        return []
    data = gzip.decompress(obj["Body"].read()).decode()
    out = []
    for line in data.splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def fetch_ledgers(since: int) -> List[Dict[str, Any]]:
    # Placeholder hook for Horizon/RPC fetching; returns list of ledger dicts.
    return []


def fetch_transactions(since: int) -> List[Dict[str, Any]]:
    return []


def fetch_operations(since: int) -> List[Dict[str, Any]]:
    return []


def fetch_events(since: int) -> List[Dict[str, Any]]:
    return []


def run_once(latest_ledger: int) -> None:
    """Pull everything since cursor and write partitioned archives."""
    cursor = load_cursor()
    since = cursor.ledger if cursor else 0

    if cursor is not None and latest_ledger < cursor.ledger:
        # testnet reset
        log.warning("testnet reset detected: latest=%s cursor=%s", latest_ledger, cursor.ledger)
        resets = _read_jsonl_gz("testnet/resets.jsonl.gz") if False else []
        try:
            obj = _client().get_object(Bucket=ARCHIVE_BUCKET, Key="testnet/resets.json")
            resets = json.loads(obj["Body"].read())
        except Exception:
            resets = []
        resets.append({"detected_at": datetime.now(timezone.utc).isoformat(),
                       "previous_cursor": cursor.ledger, "new_latest": latest_ledger})
        _client().put_object(Bucket=ARCHIVE_BUCKET, Key="testnet/resets.json",
                             Body=json.dumps(resets).encode(), ContentType="application/json")
        since = 0

    ledgers = fetch_ledgers(since)
    txs = fetch_transactions(since)
    ops = fetch_operations(since)
    evs = fetch_events(since)

    # group by hour of each record's timestamp/ledger close time
    buckets: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    def bucket_of(rec):
        ts = rec.get("closed_at") or rec.get("created_at") or datetime.now(timezone.utc).isoformat()
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now(timezone.utc)
        return _partition(dt)

    for kind, records in (("ledgers", ledgers), ("transactions", txs),
                          ("operations", ops), ("events", evs)):
        for r in records:
            b = bucket_of(r)
            buckets.setdefault(b, {"ledgers": [], "transactions": [], "operations": [], "events": []})
            buckets[b][kind].append(r)

    for part, data in buckets.items():
        for kind in ("ledgers", "transactions", "operations", "events"):
            _write_jsonl_gz(f"{part}/{kind}.jsonl.gz", data[kind])

    # manifest per day
    days = set()
    for part in buckets:
        days.add(part.rsplit("/", 1)[0])
    for day in days:
        hours = sorted({p.split("/")[-1] for p in buckets if p.rsplit("/", 1)[0] == day})
        manifest = {"day": day, "hours": hours,
                    "counts": {h: {k: len(buckets[f"{day}/{h}"][k]) for k in ("ledgers", "transactions", "operations", "events")}
                               for h in hours if f"{day}/{h}" in buckets}}
        _client().put_object(Bucket=ARCHIVE_BUCKET, Key=f"{day}/manifest.json",
                             Body