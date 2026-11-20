from pydantic import BaseModel, ConfigDict, Field

Fact = int | str | None


class ContractSnapshot(BaseModel):
    model_config = ConfigDict(
        extra="forbid", json_schema_serialization_defaults_required=True
    )

    facts: dict[str, Fact] = Field(default_factory=dict)
    items: list[str] = Field(default_factory=list)
    deadlines: dict[str, int] = Field(default_factory=dict)


class Reading(BaseModel):
    model_config = ConfigDict(
        extra="forbid", json_schema_serialization_defaults_required=True
    )

    contract: str
    subject: str
    value: str | None = None
    timestamp: int | None = None
    age_seconds: int | None = None
    stale: bool | None = None
    facts: dict[str, Fact] = Field(default_factory=dict)
