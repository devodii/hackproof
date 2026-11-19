from pydantic import BaseModel, ConfigDict, Field

Fact = int | str | None


class ContractSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    facts: dict[str, Fact] = Field(default_factory=dict)
    items: list[str] = Field(default_factory=list)


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract: str
    subject: str
    value: str
    timestamp: int | None = None
    age_seconds: int | None = None
    stale: bool | None = None
    facts: dict[str, Fact] = Field(default_factory=dict)
