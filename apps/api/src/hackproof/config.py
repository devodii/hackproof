from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from trawl.github.client import parse_tokens

ROOT = Path(__file__).resolve().parents[4]
ROOT_ENV = ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV, env_prefix="HACKPROOF_", extra="ignore"
    )

    database_url: str = Field(
        default="postgresql://hackproof:hackproof@localhost:5440/hackproof",
        validation_alias=AliasChoices("DATABASE_URL", "HACKPROOF_DATABASE_URL"),
    )
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    network_passphrase: str = "Test SDF Network ; September 2015"
    data_dir: Path = ROOT / "data"
    hackathon_file: Path = ROOT / "data" / "hackmeridian-2026" / "main.yaml"
    integrations_file: Path = ROOT / "data" / "integrations.yaml"
    friendbot_account: str = "GAIH3ULLFQ4DGSECF2AR555KZ4KNDGEKN4AFI4SU2M7B43MGK3QJZNSR"
    rpc_concurrency: int = 6
    pgschema_image: str = "pgplex/pgschema:1.14.1"
    anthropic_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "HACKPROOF_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"
        ),
    )
    chat_model: str = "claude-sonnet-5-5"
    github_tokens: Annotated[list[str], NoDecode] = Field(
        default_factory=list, validation_alias="HACKPROOF_GITHUB_TOKEN"
    )
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("github_tokens", mode="before")
    @classmethod
    def split_tokens(cls, value: object) -> object:
        return parse_tokens(value) if isinstance(value, str) else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
