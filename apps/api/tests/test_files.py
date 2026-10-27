import pytest

from hackproof.github.client import GithubUnavailable
from hackproof.github.files import BATCH, _query, fetch_texts


def test_query_escapes_paths_and_aliases_every_file():
    query = _query("team/app", "main", ['src/a "quoted".ts', "README.md"])
    assert 'f0: object(expression: "main:src/a \\"quoted\\".ts")' in query
    assert 'f1: object(expression: "main:README.md")' in query
    assert 'repository(owner: "team", name: "app")' in query


async def test_blank_and_missing_files_are_dropped():
    class Github:
        async def graphql(self, query: str) -> dict:
            return {"repository": {"f0": {"text": "hello"}, "f1": None, "f2": {"text": ""}}}

    found = await fetch_texts(Github(), "a/b", "main", ["a.md", "b.md", "c.md"])
    assert found == {"a.md": "hello"}


async def test_a_failing_batch_is_split_until_the_bad_file_is_isolated():
    class Github:
        def __init__(self) -> None:
            self.calls = 0

        async def graphql(self, query: str) -> dict:
            self.calls += 1
            if "bad.json" in query and query.count("object(") > 1:
                raise GithubUnavailable("too big")
            if "bad.json" in query:
                raise GithubUnavailable("still bad")
            paths = [p for p in ("a.md", "b.md", "c.md") if p in query]
            return {"repository": {f"f{i}": {"text": p} for i, p in enumerate(paths)}}

    with pytest.raises(GithubUnavailable):
        await fetch_texts(Github(), "a/b", "main", ["a.md", "bad.json", "b.md", "c.md"])


async def test_large_file_lists_are_sent_in_batches():
    class Github:
        def __init__(self) -> None:
            self.sizes: list[int] = []

        async def graphql(self, query: str) -> dict:
            self.sizes.append(query.count("object("))
            return {"repository": {}}

    github = Github()
    await fetch_texts(github, "a/b", "main", [f"f{i}.md" for i in range(BATCH * 2 + 3)])
    assert sorted(github.sizes) == [3, BATCH, BATCH]
