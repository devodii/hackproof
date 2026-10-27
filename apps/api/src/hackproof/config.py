from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]
ROOT_ENV = ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV, env_prefix="HACKPROOF_", extra="ignore")

    database_url: str = "postgresql://hackproof:hackproof@localhost:5440/hackproof"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    network_passphrase: str = "Test SDF Network ; September 2015"
    hackathon_file: Path = ROOT / "config" / "hackmeridian-2026.yaml"
    friendbot_account: str = "GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR"
    rpc_concurrency: int = 6
    github_tokens: Annotated[list[str], NoDecode] = Field(
        default_factory=list, validation_alias="HACKPROOF_GITHUB_TOKEN"
    )
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("github_tokens", mode="before")
    @classmethod
    def split_tokens(cls, value: object) -> object:
        if isinstance(value, str):
            return [token.strip() for token in value.split(",") if token.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
