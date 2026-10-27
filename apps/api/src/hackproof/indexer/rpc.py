import asyncio
from typing import Any

import httpx

RETRYABLE = {429, 500, 502, 503, 504}


class RpcError(Exception):
    pass


class SorobanRpc:
    def __init__(self, client: httpx.AsyncClient, url: str) -> None:
        self._client = client
        self._url = url

    async def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        for attempt in range(8):
            try:
                response = await self._client.post(self._url, json=body)
            except httpx.TransportError:
                await asyncio.sleep(2**attempt / 4)
                continue
            if response.status_code in RETRYABLE:
                await asyncio.sleep(2**attempt / 4)
                continue
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                raise RpcError(payload["error"])
            return payload["result"]
        raise RpcError(f"{method} failed after retries")

    async def transactions(
        self, *, start_ledger: int | None = None, cursor: str | None = None, limit: int = 200
    ) -> dict[str, Any]:
        pagination: dict[str, Any] = {"limit": limit}
        params: dict[str, Any] = {"pagination": pagination}
        if cursor is not None:
            pagination["cursor"] = cursor
        else:
            params["startLedger"] = start_ledger
        return await self.call("getTransactions", params)

    async def latest_ledger(self) -> int:
        return (await self.call("getHealth"))["latestLedger"]
