from pydantic import BaseModel, ConfigDict


class ContractSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base: str | None = None
    decimals: int | None = None
    resolution: int | None = None
    retention: int | None = None
    version: int | None = None
    last_timestamp: int | None = None
    assets: list[str]


class Quote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract: str
    asset: str
    price: str
    decimals: int
    timestamp: int
    age_seconds: int
    stale: bool
