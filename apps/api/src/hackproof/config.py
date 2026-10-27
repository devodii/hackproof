from datetime import datetime, timedelta
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="HACKPROOF_")

    database_url: str = "postgresql://hackproof:hackproof@localhost:5440/hackproof"
    horizon_url: str = "https://horizon-testnet.stellar.org"
    soroban_rpc_url: str = "https://soroban-testnet.stellar.org"
    network_passphrase: str = "Test SDF Network ; September 2015"
    hack_start: datetime = datetime.fromisoformat("2026-10-25T09:00:00+00:00")
    hack_duration_hours: int = 27
    pull_lead_minutes: int = 60
    rpc_concurrency: int = 6
    github_token: str | None = None
    cors_origins: list[str] = ["http://localhost:5173"]

    @property
    def pull_start(self) -> datetime:
        return self.hack_start - timedelta(minutes=self.pull_lead_minutes)

    @property
    def hack_end(self) -> datetime:
        return self.hack_start + timedelta(hours=self.hack_duration_hours)


@lru_cache
def get_settings() -> Settings:
    return Settings()
