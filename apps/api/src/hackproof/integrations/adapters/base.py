from abc import ABC, abstractmethod
from typing import ClassVar

import httpx

from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot, Reading


class Adapter(ABC):
    name: ClassVar[str]

    @abstractmethod
    async def observe(
        self, http: httpx.AsyncClient, network: Network, contract: ProfileContract
    ) -> ContractSnapshot | None: ...

    async def probe(
        self,
        http: httpx.AsyncClient,
        network: Network,
        contract: ProfileContract,
        subject: str,
        params: dict[str, int],
    ) -> Reading | None:
        return None
