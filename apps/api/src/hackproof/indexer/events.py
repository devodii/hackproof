from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    model_config = ConfigDict(frozen=True)
    table: ClassVar[str]

    def row(self) -> tuple[Any, ...]:
        raise NotImplementedError


class Deploy(Event):
    table: ClassVar[str] = "contracts"
    contract_id: str
    deployer: str
    wasm_hash: str
    tx_hash: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (self.contract_id, self.deployer, self.wasm_hash, self.tx_hash, self.ledger, self.at)


class Upload(Event):
    table: ClassVar[str] = "wasm_uploads"
    wasm_hash: str
    uploader: str
    size: int
    meta: dict[str, str]
    tx_hash: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (
            self.tx_hash,
            self.wasm_hash,
            self.uploader,
            self.size,
            self.meta.get("source_repo"),
            self.meta,
            self.ledger,
            self.at,
        )


class Failure(Event):
    table: ClassVar[str] = "failed_txs"
    tx_hash: str
    source_account: str
    kind: str
    result_code: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (
            self.tx_hash,
            self.source_account,
            self.kind,
            self.result_code,
            self.ledger,
            self.at,
        )


class Funding(Event):
    table: ClassVar[str] = "accounts"
    account: str
    funder: str
    tx_hash: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (self.account, self.funder, self.tx_hash, self.ledger, self.at)


class ClassicOp(Event):
    table: ClassVar[str] = "classic_ops"
    tx_hash: str
    index: int
    source_account: str
    op_type: str
    asset: str | None
    counterparty: str | None
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (
            self.tx_hash,
            self.index,
            self.source_account,
            self.op_type,
            self.asset,
            self.counterparty,
            self.ledger,
            self.at,
        )
