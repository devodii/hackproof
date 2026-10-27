from hackproof.github.history import stellar_added_in_window

WANTED = {"js": ["@stellar/stellar-sdk"]}
HEAD = {"package.json": '{"dependencies": {"@stellar/stellar-sdk": "14.0.0"}}'}


class FakeGithub:
    def __init__(self, earlier: dict[str, bytes]) -> None:
        self._earlier = earlier

    async def raw(self, full_name: str, ref: str, path: str) -> bytes | None:
        return self._earlier.get(path)


async def added(base_sha: str | None, earlier: dict[str, bytes]) -> bool:
    return await stellar_added_in_window(FakeGithub(earlier), "a/b", HEAD, WANTED, base_sha)


async def test_a_repo_with_no_history_before_the_window_was_born_inside_it():
    assert await added(None, {})


async def test_a_dependency_missing_before_the_window_was_added_during_it():
    before = {"package.json": b'{"dependencies": {"react": "19"}}'}
    assert await added("abc", before)


async def test_a_manifest_that_did_not_exist_before_counts_as_added():
    assert await added("abc", {})


async def test_a_dependency_already_present_before_the_window_is_not_new():
    before = {"package.json": b'{"dependencies": {"@stellar/stellar-sdk": "13.0.0"}}'}
    assert not await added("abc", before)
