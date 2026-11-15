import sys
from typing import Self
from urllib.parse import parse_qs, quote, unquote, urlparse

from pydantic import BaseModel

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}


class Connection(BaseModel):
    """One database, as pgschema's container needs to reach it."""

    host: str
    port: int = 5432
    user: str
    password: str
    database: str
    sslmode: str = "prefer"

    @classmethod
    def from_url(cls, url: str) -> Self:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        return cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            user=unquote(parsed.username or ""),
            password=unquote(parsed.password or ""),
            database=parsed.path.lstrip("/"),
            sslmode=query.get("sslmode", ["prefer"])[0],
        )

    @property
    def is_local(self) -> bool:
        return self.host in LOCAL_HOSTS

    @property
    def label(self) -> str:
        return f"{self.user}@{self.host}:{self.port}/{self.database}"

    def mask_lines(self) -> list[str]:
        """Workflow commands that keep this database out of public CI logs."""
        secrets = {self.host, self.user, self.password, quote(self.password, safe="")}
        return [f"::add-mask::{value}" for value in sorted(secrets) if value]

    def container_route(self) -> tuple[list[str], str]:
        """Docker network flags and the host name the container should dial."""
        if not self.is_local:
            return [], self.host
        if sys.platform == "linux":
            return ["--network", "host"], "localhost"
        return [
            "--add-host",
            "host.docker.internal:host-gateway",
        ], "host.docker.internal"
