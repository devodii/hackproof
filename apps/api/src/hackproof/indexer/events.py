import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar


@dataclass(frozen=True)
class Deploy:
    table: ClassVar[str] = "contracts"
    contract_id: str
    deployer: str
    wasm_hash: str
    tx_hash: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (self.contract_id, self.deployer, self.wasm_hash, self.tx_hash, self.ledger, self.at)


@dataclass(frozen=True)
class Upload:
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
            json.dumps(self.meta),
            self.ledger,
            self.at,
        )


@dataclass(frozen=True)
class Failure:
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


@dataclass(frozen=True)
class Funding:
    table: ClassVar[str] = "accounts"
    account: str
    funder: str
    tx_hash: str
    ledger: int
    at: datetime

    def row(self) -> tuple[Any, ...]:
        return (self.account, self.funder, self.tx_hash, self.ledger, self.at)


@dataclass(frozen=True)
class ClassicOp:
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


Event = Deploy | Upload | Failure | Funding | ClassicOp
