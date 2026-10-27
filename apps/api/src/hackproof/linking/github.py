from dataclasses import dataclass

import httpx

API = "https://api.github.com"


@dataclass(frozen=True)
class GithubRepo:
    full_name: str
    url: str
    description: str | None
    stars: int
    owner: str
    owner_avatar: str | None
    owner_location: str | None


class GithubClient:
    def __init__(self, client: httpx.AsyncClient, token: str | None) -> None:
        self._client = client
        self._headers = {"Accept": "application/vnd.github+json"}
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    async def _get(self, path: str) -> dict | None:
        response = await self._client.get(f"{API}{path}", headers=self._headers)
        if response.status_code in (403, 404, 451):
            return None
        response.raise_for_status()
        return response.json()

    async def repo(self, full_name: str) -> GithubRepo | None:
        data = await self._get(f"/repos/{full_name}")
        if data is None:
            return None
        owner = await self._get(f"/users/{data['owner']['login']}")
        return GithubRepo(
            full_name=data["full_name"],
            url=data["html_url"],
            description=data["description"],
            stars=data["stargazers_count"],
            owner=data["owner"]["login"],
            owner_avatar=data["owner"]["avatar_url"],
            owner_location=owner["location"] if owner else None,
        )
