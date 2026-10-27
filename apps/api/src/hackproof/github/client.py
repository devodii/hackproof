import asyncio
import time
from typing import Any, Literal

import httpx
from pydantic import BaseModel

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
SEARCH_INTERVAL = {"code": 6.5, "repositories": 2.2}

Search = Literal["code", "repositories"]


class Token(BaseModel):
    value: str | None
    remaining: int = 5000
    blocked_until: float = 0.0
    next_search_at: float = 0.0
    requests: int = 0


class GithubClient:
    def __init__(self, http: httpx.AsyncClient, tokens: list[str]) -> None:
        self._http = http
        self._tokens = [Token(value=value) for value in tokens] or [Token(value=None)]
        self._lock = asyncio.Lock()

    async def _acquire(self, search: Search | None) -> Token:
        while True:
            async with self._lock:
                now = time.monotonic()
                usable = [t for t in self._tokens if t.blocked_until <= now and t.remaining > 20]
                if usable and search is None:
                    return max(usable, key=lambda t: t.remaining)
                if usable:
                    token = min(usable, key=lambda t: t.next_search_at)
                    start = max(token.next_search_at, now)
                    token.next_search_at = start + SEARCH_INTERVAL[search]
                    wait = start - now
                else:
                    token = None
                    wait = max(min(t.blocked_until for t in self._tokens) - now, 1)
            await asyncio.sleep(wait)
            if token is not None:
                return token

    @staticmethod
    def _record(token: Token, response: httpx.Response) -> None:
        token.requests += 1
        remaining = response.headers.get("x-ratelimit-remaining")
        if remaining is not None and response.headers.get("x-ratelimit-resource") == "core":
            token.remaining = int(remaining)
        if response.status_code in (403, 429) and remaining == "0":
            reset = int(response.headers.get("x-ratelimit-reset", time.time() + 60))
            token.blocked_until = time.monotonic() + max(reset - time.time(), 1)
        elif response.status_code in (403, 429) and "retry-after" in response.headers:
            token.blocked_until = time.monotonic() + int(response.headers["retry-after"])

    async def get(
        self, path: str, params: dict[str, Any] | None = None, *, search: Search | None = None
    ) -> httpx.Response | None:
        for _ in range(6):
            token = await self._acquire(search)
            headers = {"Accept": "application/vnd.github+json"}
            if token.value:
                headers["Authorization"] = f"Bearer {token.value}"
            try:
                response = await self._http.get(f"{API}{path}", params=params, headers=headers)
            except httpx.TransportError:
                await asyncio.sleep(2)
                continue
            self._record(token, response)
            if response.status_code in (403, 429, 502, 503):
                continue
            if response.status_code in (404, 409, 451):
                return None
            response.raise_for_status()
            return response
        return None

    async def json(
        self, path: str, params: dict[str, Any] | None = None, *, search: Search | None = None
    ) -> Any | None:
        response = await self.get(path, params, search=search)
        return response.json() if response is not None else None

    async def raw(self, full_name: str, ref: str, path: str, limit: int = 512_000) -> bytes | None:
        try:
            response = await self._http.get(f"{RAW}/{full_name}/{ref}/{path}")
        except httpx.TransportError:
            return None
        if response.status_code != 200 or len(response.content) > limit:
            return None
        return response.content
