from datetime import UTC, datetime

from hackproof.github.discovery import is_pinned, parse_seeds, should_keep
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


def test_pinned_repos_bypass_every_filter():
    stale = candidate(
        pushed_at=datetime(2025, 1, 1, tzinfo=UTC), fork=True, discovered_via={"seed:discord"}
    )
    assert is_pinned(stale)
    assert should_keep(stale, WINDOW, DISCOVERY)


def test_parse_seeds_reads_urls_and_tags():
    text = "# header\n\nhttps://github.com/a/b discord\ngithub:c/d\nnot a repo\n"
    assert parse_seeds(text) == [("a/b", "discord"), ("c/d", "manual")]
