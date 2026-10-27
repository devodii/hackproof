from datetime import UTC, datetime

import httpx


class Horizon:
    def __init__(self, client: httpx.AsyncClient, url: str) -> None:
        self._client = client
        self._url = url

    async def closed_at(self, sequence: int) -> datetime:
        response = await self._client.get(f"{self._url}/ledgers/{sequence}")
        response.raise_for_status()
        raw = response.json()["closed_at"]
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(UTC)

    async def first_ledger_at_or_after(self, moment: datetime, low: int, high: int) -> int:
        while low < high:
            middle = (low + high) // 2
            if await self.closed_at(middle) < moment:
                low = middle + 1
            else:
                high = middle
        return low
