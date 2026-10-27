from urllib.parse import parse_qs, urlparse

from hackproof.github.client import GithubClient


async def count_commits(github: GithubClient, full_name: str, **params: str) -> int | None:
    response = await github.get(f"/repos/{full_name}/commits", {"per_page": 1, **params})
    if response is None:
        return None
    last = response.links.get("last")
    if last:
        return int(parse_qs(urlparse(last["url"]).query)["page"][0])
    return len(response.json())
