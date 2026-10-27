import asyncio
import time
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
SEARCH_INTERVAL = {"code": 6.5, "repositories": 2.2}
RETRYABLE = {403, 429, 500, 502, 503, 504}
ABSENT = {404, 409, 451}
ATTEMPTS = 6

Search = Literal["code", "repositories"]
Resource = Literal["core", "graphql"]


class GithubUnavailable(Exception):
    pass


class Token(BaseModel):
    value: str | None
    budget: dict[str, int] = Field(default_factory=lambda: {"core": 5000, "graphql": 5000})
    blocked_until: float = 0.0
    next_search_at: dict[str, float] = Field(
        default_factory=lambda: {"code": 0.0, "repositories": 0.0}
    )


class GithubClient:
    def __init__(self, http: httpx.AsyncClient, tokens: list[str]) -> None:
        self._http = http
        self._tokens = [Token(value=value) for value in tokens] or [Token(value=None)]
        self._lock = asyncio.Lock()

    async def _acquire(self, search: Search | None, resource: Resource) -> Token:
        while True:
            async with self._lock:
                now = time.monotonic()
                usable = [
                    t for t in self._tokens if t.blocked_until <= now and t.budget[resource] > 20
                ]
                if usable and search is None:
                    return max(usable, key=lambda t: t.budget[resource])
                if usable:
                    token = min(usable, key=lambda t: t.next_search_at[search])
                    start = max(token.next_search_at[search], now)
                    token.next_search_at[search] = start + SEARCH_INTERVAL[search]
                    wait = start - now
                else:
                    token = None
                    wait = max(min(t.blocked_until for t in self._tokens) - now, 1)
            await asyncio.sleep(wait)
            if token is not None:
                return token

    @staticmethod
    def _record(token: Token, response: httpx.Response) -> None:
        remaining = response.headers.get("x-ratelimit-remaining")
        resource = response.headers.get("x-ratelimit-resource")
        if remaining is not None and resource in token.budget:
            token.budget[resource] = int(remaining)
        if response.status_code in (403, 429) and remaining == "0":
            reset = int(response.headers.get("x-ratelimit-reset", time.time() + 60))
            token.blocked_until = time.monotonic() + max(reset - time.time(), 1)
        elif response.status_code in (403, 429) and "retry-after" in response.headers:
            token.blocked_until = time.monotonic() + int(response.headers["retry-after"])

    async def _send(
        self,
        method: str,
        url: str,
        *,
        search: Search | None = None,
        resource: Resource = "core",
        **options: Any,
    ) -> httpx.Response:
        for attempt in range(ATTEMPTS):
            token = await self._acquire(search, resource)
            headers = {"Accept": "application/vnd.github+json"}
            if token.value:
                headers["Authorization"] = f"Bearer {token.value}"
            try:
                response = await self._http.request(method, url, headers=headers, **options)
            except httpx.TransportError:
                await asyncio.sleep(2**attempt / 2)
                continue
            self._record(token, response)
            if response.status_code in RETRYABLE:
                await asyncio.sleep(2**attempt / 4)
                continue
            return response
        raise GithubUnavailable(url)

    async def get(
        self, path: str, params: dict[str, Any] | None = None, *, search: Search | None = None
    ) -> httpx.Response | None:
        response = await self._send("GET", f"{API}{path}", search=search, params=params)
        if response.status_code in ABSENT:
            return None
        response.raise_for_status()
        return response

    async def json(
        self, path: str, params: dict[str, Any] | None = None, *, search: Search | None = None
    ) -> Any | None:
        response = await self.get(path, params, search=search)
        if response is None or response.status_code == 204:
            return None
        return response.json()

    async def graphql(self, query: str) -> dict[str, Any]:
        response = await self._send(
            "POST", f"{API}/graphql", resource="graphql", json={"query": query}
        )
        response.raise_for_status()
        payload = response.json()
        errors = [e for e in payload.get("errors", []) if e.get("type") != "NOT_FOUND"]
        if errors:
            raise GithubUnavailable(errors[0].get("message", "graphql error"))
        return payload["data"]

    async def raw(self, full_name: str, ref: str, path: str, limit: int = 512_000) -> bytes | None:
        url = f"{RAW}/{full_name}/{ref}/{path}"
        for attempt in range(ATTEMPTS):
            try:
                response = await self._http.get(url)
            except httpx.TransportError:
                await asyncio.sleep(2**attempt / 2)
                continue
            if response.status_code in RETRYABLE:
                await asyncio.sleep(2**attempt / 2)
                continue
            if response.status_code != 200 or len(response.content) > limit:
                return None
            return response.content
        raise GithubUnavailable(url)
