from datetime import datetime, timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="HACKPROOF_")

    database_path: str = "hackproof.db"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    network_passphrase: str = "Test SDF Network ; September 2015"
    hack_start: datetime = datetime.fromisoformat("2026-01-01T00:00:00+00:00")
    hack_duration_hours: int = 27
    github_token: str | None = None
    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def hack_end(self) -> datetime:
        return self.hack_start + timedelta(hours=self.hack_duration_hours)


@lru_cache
def get_settings() -> Settings:
    return Settings()
