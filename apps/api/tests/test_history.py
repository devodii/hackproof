from datetime import UTC, datetime

from hackproof.github.history import stellar_added_in_window

WANTED = {"js": ["@stellar/stellar-sdk"]}
END = datetime(2026, 10, 26, 12, tzinfo=UTC)
WITH = b'{"dependencies": {"@stellar/stellar-sdk": "14.0.0"}}'
WITHOUT = b'{"dependencies": {"react": "19"}}'


class FakeGithub:
    def __init__(self, commits: list[str], repo: dict[str, dict[str, bytes]]) -> None:
        self._commits = commits
        self._repo = repo

    async def json(self, path: str, params: dict | None = None):
        if path.endswith("/commits"):
            return [{"sha": sha} for sha in self._commits]
        sha = path.rsplit("/", 1)[-1]
        return {
            "tree": [{"type": "blob", "path": name} for name in self._repo.get(sha, {})]
        }

    async def raw(self, full_name: str, ref: str, path: str) -> bytes | None:
        return self._repo.get(ref, {}).get(path)


async def added(base_sha: str | None, commits: list[str], repo: dict) -> bool:
    return await stellar_added_in_window(
        FakeGithub(commits, repo), "a/b", WANTED, base_sha, END
    )


async def test_stellar_missing_at_the_window_start_and_present_at_its_end_was_added_inside_it():
    repo = {"start": {"package.json": WITHOUT}, "end": {"package.json": WITH}}
    assert await added("start", ["end"], repo)


async def test_a_repo_with_no_history_before_the_window_was_born_inside_it():
    assert await added(None, ["end"], {"end": {"package.json": WITH}})


async def test_stellar_already_present_at_the_window_start_is_not_new():
    repo = {"start": {"package.json": WITH}, "end": {"package.json": WITH}}
    assert not await added("start", ["end"], repo)


async def test_stellar_added_only_after_the_window_ended_does_not_count():
    repo = {"start": {"package.json": WITHOUT}, "end": {"package.json": WITHOUT}}
    assert not await added("start", ["end"], repo)


async def test_a_repo_with_no_commit_by_the_window_end_does_not_count():
    assert not await added(None, [], {})
