from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[4]
ROOT_ENV = ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV, env_prefix="HACKPROOF_", extra="ignore")

    database_url: str = "postgresql://hackproof:hackproof@localhost:5440/hackproof"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    network_passphrase: str = "Test SDF Network ; September 2015"
    hackathon_file: Path = ROOT / "config" / "hackmeridian-2026.yaml"
    friendbot_account: str = "GBZXN7PIRZGNMHGA7MUUUF4GWPY5AYPV6LY4UV2GL6VJGIQRXFDNMADI"
    rpc_concurrency: int = 6
    github_token: str | None = None
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
