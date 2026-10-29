from datetime import UTC, datetime

from hackproof.github import discovery
from hackproof.github.client import GithubUnavailable
from hackproof.github.discovery import is_pinned, patient, should_keep, split_range
from hackproof.github.models import Candidate
from hackproof.hackathon import Discovery, Window

WINDOW = Window(
    start=datetime(2026, 10, 25, 9, tzinfo=UTC),
    pull_start=datetime(2026, 10, 25, 8, tzinfo=UTC),
    end=datetime(2026, 10, 26, 12, tzinfo=UTC),
)
DISCOVERY = Discovery(
    github_queries=[],
    github_code_queries=[],
    github_string_queries=[],
    dependency_fingerprints={},
    exclude_owners=["stellar"],
    known_infra_accounts=[],
)


def candidate(**overrides) -> Candidate:
    fields = {
        "full_name": "team/app",
        "url": "https://github.com/team/app",
        "owner": "team",
        "pushed_at": datetime(2026, 10, 26, tzinfo=UTC),
        "discovered_via": {"search:x"},
    }
    return Candidate(**{**fields, **overrides})


def test_keeps_repos_pushed_around_the_window():
    assert should_keep(candidate(), WINDOW, DISCOVERY)


def test_drops_stale_forked_and_excluded_repos():
    assert not should_keep(candidate(pushed_at=datetime(2026, 9, 1, tzinfo=UTC)), WINDOW, DISCOVERY)
    assert not should_keep(candidate(fork=True), WINDOW, DISCOVERY)
    assert not should_keep(candidate(owner="Stellar"), WINDOW, DISCOVERY)


def test_repos_named_in_wasm_metadata_bypass_every_filter():
    stale = candidate(
        pushed_at=datetime(2025, 1, 1, tzinfo=UTC), fork=True, discovered_via={"wasm_meta"}
    )
    assert is_pinned(stale)
    assert should_keep(stale, WINDOW, DISCOVERY)


async def test_split_range_slices_until_every_range_fits_the_cap():
    matches = [value for value in range(0, 10_000, 7)]

    async def count(lo: int, hi: int) -> int:
        return sum(1 for value in matches if lo <= value <= hi)

    ranges = await split_range(0, 10_000, count, cap=100)
    counts = [await count(lo, hi) for lo, hi in ranges]

    assert max(counts) <= 100
    assert sum(counts) == len(matches)
    assert ranges[0][0] == 0 and ranges[-1][1] == 10_000
    assert all(a[1] + 1 == b[0] for a, b in zip(ranges, ranges[1:], strict=False))


async def test_split_range_stops_at_a_single_value_even_when_over_the_cap():
    async def count(lo: int, hi: int) -> int:
        return 5_000

    assert await split_range(7, 7, count, cap=10) == [(7, 7)]


async def test_split_range_leaves_small_queries_whole():
    async def count(lo: int, hi: int) -> int:
        return 3

    assert await split_range(0, 400_000, count) == [(0, 400_000)]


async def test_a_query_survives_a_connection_outage(monkeypatch):
    async def instant(_seconds):
        return None

    monkeypatch.setattr(discovery.asyncio, "sleep", instant)
    runs: list[str] = []

    async def flaky(query: str) -> None:
        runs.append(query)
        if len(runs) < 3:
            raise GithubUnavailable(query)

    await patient("q", flaky)

    assert runs == ["q", "q", "q"]


async def test_a_query_that_never_recovers_is_skipped_not_fatal(monkeypatch):
    async def instant(_seconds):
        return None

    monkeypatch.setattr(discovery.asyncio, "sleep", instant)

    async def down(query: str) -> None:
        raise GithubUnavailable(query)

    await patient("q", down)
