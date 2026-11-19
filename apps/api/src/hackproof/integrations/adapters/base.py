from abc import ABC, abstractmethod
from typing import ClassVar

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot, Reading


class Adapter(ABC):
    name: ClassVar[str]

    @abstractmethod
    async def observe(
        self, rpc: SorobanRpc, network: Network, contract: ProfileContract
    ) -> ContractSnapshot | None: ...

    async def probe(
        self,
        rpc: SorobanRpc,
        network: Network,
        contract: ProfileContract,
        subject: str,
        params: dict[str, int],
    ) -> Reading | None:
        return None
