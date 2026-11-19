from abc import ABC, abstractmethod
from typing import ClassVar

from hackproof.indexer.rpc import SorobanRpc
from hackproof.integrations.catalog import Network, ProfileContract
from hackproof.integrations.chain import ContractSnapshot, Quote


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
        asset: str,
        params: dict[str, int],
    ) -> Quote | None:
        return None
